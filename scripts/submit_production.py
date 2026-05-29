import os
import re
import sys
import time
from pathlib import Path

import jwt
import requests

KEY_ID = os.environ["ASC_KEY_ID"]
ISSUER_ID = os.environ["ASC_ISSUER_ID"]
APP_BUNDLE_ID = os.environ.get("APP_BUNDLE_ID", "com.tokyonasu.puchipuchi")
APP_VERSION = os.environ.get("APP_VERSION", "1.0")
BUILD_NUMBER = os.environ["BUILD_NUMBER"]
P8_PATH = os.environ.get("ASC_P8_PATH", "/tmp/asc_key.p8")


def make_token():
    now = int(time.time())
    private_key = Path(P8_PATH).read_text(encoding="utf-8")
    return jwt.encode(
        {"iss": ISSUER_ID, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"},
        private_key,
        algorithm="ES256",
        headers={"kid": KEY_ID},
    )


def api(method, path, **kwargs):
    last = None
    for _ in range(6):
        last = requests.request(
            method,
            f"https://api.appstoreconnect.apple.com/v1{path}",
            headers={"Authorization": f"Bearer {make_token()}", "Content-Type": "application/json"},
            timeout=120,
            **kwargs,
        )
        if last.status_code not in (401, 429, 500, 502, 503, 504):
            return last
        time.sleep(20)
    return last


def api_json(method, path, **kwargs):
    response = api(method, path, **kwargs)
    try:
        body = response.json()
    except Exception:
        body = {}
    return response, body


def list_all(path):
    rows = []
    next_path = path
    while next_path:
        response, body = api_json("GET", next_path)
        if response.status_code != 200:
            raise RuntimeError(f"List failed {response.status_code}: {response.text[:500]}")
        rows.extend(body.get("data", []))
        next_url = body.get("links", {}).get("next")
        next_path = next_url.split("/v1", 1)[1] if next_url and "/v1" in next_url else None
    return rows


def find_app_id():
    response, body = api_json("GET", f"/apps?filter[bundleId]={APP_BUNDLE_ID}&limit=1")
    if response.status_code != 200 or not body.get("data"):
        raise RuntimeError(f"App not found for bundle ID: {APP_BUNDLE_ID}")
    return body["data"][0]["id"]


def find_version_id(app_id):
    versions = list_all(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=200")
    for version in versions:
        attrs = version.get("attributes", {})
        if attrs.get("versionString") == APP_VERSION:
            print(f"Found version {APP_VERSION}: {version['id']} state={attrs.get('appStoreState')}")
            return version["id"]
    raise RuntimeError(f"App Store version not found: {APP_VERSION}")


def wait_for_build(app_id):
    for attempt in range(1, 91):
        response, body = api_json(
            "GET",
            f"/builds?filter[app]={app_id}&filter[version]={BUILD_NUMBER}&filter[processingState]=VALID&limit=1",
        )
        if response.status_code == 200 and body.get("data"):
            build_id = body["data"][0]["id"]
            print(f"Build ready: {build_id}")
            return build_id
        print(f"Waiting for build processing... {attempt}/90")
        time.sleep(30)
    raise RuntimeError(f"Build {BUILD_NUMBER} did not finish processing.")


def assign_build(version_id, build_id):
    api(
        "PATCH",
        f"/builds/{build_id}",
        json={"data": {"type": "builds", "id": build_id, "attributes": {"usesNonExemptEncryption": False}}},
    )
    response = api(
        "PATCH",
        f"/appStoreVersions/{version_id}/relationships/build",
        json={"data": {"type": "builds", "id": build_id}},
    )
    if response.status_code not in (200, 204):
        raise RuntimeError(f"Build assign failed {response.status_code}: {response.text[:1000]}")
    print(f"Build assigned: {response.status_code}")


def open_submission_id(app_id):
    response, body = api_json("GET", f"/apps/{app_id}/reviewSubmissions?limit=20")
    if response.status_code != 200:
        return None
    for submission in body.get("data", []):
        state = submission.get("attributes", {}).get("state")
        if state == "READY_FOR_REVIEW":
            return submission["id"]
    return None


def cancel_unresolved_submissions(app_id):
    response, body = api_json("GET", f"/apps/{app_id}/reviewSubmissions?limit=20")
    if response.status_code != 200:
        return
    for submission in body.get("data", []):
        if submission.get("attributes", {}).get("state") != "UNRESOLVED_ISSUES":
            continue
        response = api(
            "PATCH",
            f"/reviewSubmissions/{submission['id']}",
            json={
                "data": {
                    "type": "reviewSubmissions",
                    "id": submission["id"],
                    "attributes": {"canceled": True},
                }
            },
        )
        print(f"Cancel unresolved review submission {submission['id']}: {response.status_code}")
        for attempt in range(1, 21):
            response, body = api_json("GET", f"/reviewSubmissions/{submission['id']}")
            state = body.get("data", {}).get("attributes", {}).get("state")
            print(f"Waiting for cancellation... {attempt}/20 state={state}")
            if state != "CANCELING":
                break
            time.sleep(15)


def create_submission(app_id):
    existing_id = open_submission_id(app_id)
    if existing_id:
        return existing_id
    response, body = api_json(
        "POST",
        "/reviewSubmissions",
        json={
            "data": {
                "type": "reviewSubmissions",
                "attributes": {"platform": "IOS"},
                "relationships": {"app": {"data": {"type": "apps", "id": app_id}}},
            }
        },
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Review submission create failed {response.status_code}: {response.text[:1000]}")
    return body["data"]["id"]


def add_review_item(submission_id, version_id):
    for attempt in range(1, 31):
        response = api(
            "POST",
            "/reviewSubmissionItems",
            json={
                "data": {
                    "type": "reviewSubmissionItems",
                    "relationships": {
                        "reviewSubmission": {"data": {"type": "reviewSubmissions", "id": submission_id}},
                        "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}},
                    },
                }
            },
        )
        print(f"Review item {attempt}/30: {response.status_code}")
        if response.status_code == 201:
            return submission_id
        if response.status_code == 409 and "ITEM_PART_OF_ANOTHER_SUBMISSION" in response.text:
            match = re.search(r"reviewSubmission with id ([0-9a-f-]+)", response.text)
            if match:
                return match.group(1)
        if response.status_code == 409 and "SCREENSHOT_UPLOADS_IN_PROGRESS" in response.text:
            time.sleep(60)
            continue
        if response.status_code != 409:
            raise RuntimeError(f"Review item failed {response.status_code}: {response.text[:1000]}")
        time.sleep(60)
    raise RuntimeError(f"Review item blocked: {response.text[:1000]}")


def finish_submission(submission_id):
    for attempt in range(1, 31):
        response, body = api_json(
            "PATCH",
            f"/reviewSubmissions/{submission_id}",
            json={
                "data": {
                    "type": "reviewSubmissions",
                    "id": submission_id,
                    "attributes": {"submitted": True},
                }
            },
        )
        print(f"Submit review {attempt}/30: {response.status_code}")
        if response.status_code == 200:
            print(f"Submitted for App Review: {body['data']['attributes'].get('state')}")
            return
        time.sleep(60)
    raise RuntimeError(f"Submit review failed {response.status_code}: {response.text[:1000]}")


def main():
    app_id = find_app_id()
    version_id = find_version_id(app_id)
    build_id = wait_for_build(app_id)
    assign_build(version_id, build_id)
    print("Waiting for App Store Connect to settle...")
    time.sleep(300)
    cancel_unresolved_submissions(app_id)
    submission_id = create_submission(app_id)
    submission_id = add_review_item(submission_id, version_id)
    finish_submission(submission_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
