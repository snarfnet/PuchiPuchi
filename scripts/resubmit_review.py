import re
import time

import jwt
import requests

KEY_ID = "WDXGY9WX55"
ISSUER = "2be0734f-943a-4d61-9dc9-5d9045c46fec"
APP_ID = "6772969864"
APP_VERSION = "1.0"

p8 = open("/tmp/asc_key.p8", encoding="utf-8").read()


def make_token():
    return jwt.encode(
        {"iss": ISSUER, "iat": int(time.time()), "exp": int(time.time()) + 1200, "aud": "appstoreconnect-v1"},
        p8,
        algorithm="ES256",
        headers={"kid": KEY_ID},
    )


def api(method, path, **kwargs):
    return requests.request(
        method,
        f"https://api.appstoreconnect.apple.com/v1{path}",
        headers={"Authorization": "Bearer " + make_token(), "Content-Type": "application/json"},
        timeout=120,
        **kwargs,
    )


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
        response.raise_for_status()
        rows.extend(body.get("data", []))
        next_url = body.get("links", {}).get("next")
        next_path = next_url.split("/v1", 1)[1] if next_url and "/v1" in next_url else None
    return rows


def find_version_id():
    versions = list_all(f"/apps/{APP_ID}/appStoreVersions?filter[platform]=IOS&limit=200")
    for version in versions:
        attrs = version.get("attributes", {})
        if attrs.get("versionString") == APP_VERSION:
            print(f"Version {version['id']} state={attrs.get('appStoreState')}")
            return version["id"]
    raise RuntimeError(f"Version not found: {APP_VERSION}")


def existing_submission_id():
    response, body = api_json("GET", f"/apps/{APP_ID}/reviewSubmissions?limit=20")
    if response.status_code != 200:
        return None
    for submission in body.get("data", []):
        state = submission.get("attributes", {}).get("state")
        if state in ("READY_FOR_REVIEW", "UNRESOLVED_ISSUES"):
            return submission["id"]
    return None


def create_submission():
    submission_id = existing_submission_id()
    if submission_id:
        return submission_id
    response, body = api_json(
        "POST",
        "/reviewSubmissions",
        json={
            "data": {
                "type": "reviewSubmissions",
                "attributes": {"platform": "IOS"},
                "relationships": {"app": {"data": {"type": "apps", "id": APP_ID}}},
            }
        },
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Create submission failed {response.status_code}: {response.text[:1000]}")
    return body["data"]["id"]


def add_item(submission_id, version_id):
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
        raise RuntimeError(f"Review item blocked {response.status_code}: {response.text[:1000]}")
    raise RuntimeError(f"Review item blocked: {response.text[:1000]}")


def submit(submission_id):
    for attempt in range(1, 4):
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
        print(f"Submit {attempt}/3: {response.status_code}")
        if response.status_code == 200:
            print(f"Submitted: {body['data']['attributes'].get('state')}")
            return
        print(response.text[:1000])
        time.sleep(60)
    raise RuntimeError(f"Submit failed {response.status_code}: {response.text[:1000]}")


version_id = find_version_id()
submission_id = create_submission()
submission_id = add_item(submission_id, version_id)
submit(submission_id)
