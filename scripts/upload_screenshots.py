import hashlib
import os
import sys
import time

import jwt
import requests

KEY_ID = "WDXGY9WX55"
ISSUER = "2be0734f-943a-4d61-9dc9-5d9045c46fec"
APP_ID = "6772969864"

SCREENSHOT_SETS = {
    "APP_IPHONE_67": ["iphone67_01.png", "iphone67_02.png", "iphone67_03.png"],
    "APP_IPHONE_65": ["iphone65_01.png", "iphone65_02.png", "iphone65_03.png"],
    "APP_IPHONE_55": ["iphone55_01.png", "iphone55_02.png", "iphone55_03.png"],
    "APP_IPAD_PRO_3GEN_129": ["ipad_01.png", "ipad_02.png", "ipad_03.png"],
}

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
        timeout=60,
        **kwargs,
    )


def list_all(path):
    items = []
    next_path = path
    while next_path:
        response = api("GET", next_path)
        response.raise_for_status()
        body = response.json()
        items.extend(body.get("data", []))
        next_url = body.get("links", {}).get("next")
        next_path = next_url.split("/v1", 1)[1] if next_url and "/v1" in next_url else None
    return items


def get_or_create_set(localization_id, display_type):
    for item in list_all(f"/appStoreVersionLocalizations/{localization_id}/appScreenshotSets?limit=200"):
        if item.get("attributes", {}).get("screenshotDisplayType") == display_type:
            return item["id"]
    response = api(
        "POST",
        "/appScreenshotSets",
        json={
            "data": {
                "type": "appScreenshotSets",
                "attributes": {"screenshotDisplayType": display_type},
                "relationships": {
                    "appStoreVersionLocalization": {
                        "data": {"type": "appStoreVersionLocalizations", "id": localization_id}
                    }
                },
            }
        },
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Create screenshot set failed: {response.status_code} {response.text[:500]}")
    return response.json()["data"]["id"]


def clear_set(set_id):
    screenshots = list_all(f"/appScreenshotSets/{set_id}/appScreenshots?limit=200")
    for screenshot in screenshots:
        response = api("DELETE", f"/appScreenshots/{screenshot['id']}")
        if response.status_code not in (200, 204):
            print(f"  delete warning {response.status_code}: {response.text[:160]}")
    if screenshots:
        print(f"  cleared {len(screenshots)} old screenshots")


def upload_screenshot(set_id, path):
    file_data = open(path, "rb").read()
    checksum = hashlib.md5(file_data).hexdigest()
    response = api(
        "POST",
        "/appScreenshots",
        json={
            "data": {
                "type": "appScreenshots",
                "attributes": {"fileName": os.path.basename(path), "fileSize": len(file_data)},
                "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}},
            }
        },
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Reserve screenshot failed: {response.status_code} {response.text[:500]}")
    screenshot = response.json()["data"]
    for op in screenshot["attributes"]["uploadOperations"]:
        headers = {h["name"]: h["value"] for h in op["requestHeaders"]}
        chunk = file_data[op["offset"] : op["offset"] + op["length"]]
        put = requests.put(op["url"], headers=headers, data=chunk, timeout=120)
        if put.status_code not in (200, 201):
            raise RuntimeError(f"Upload chunk failed: {put.status_code} {put.text[:300]}")
    response = api(
        "PATCH",
        f"/appScreenshots/{screenshot['id']}",
        json={
            "data": {
                "type": "appScreenshots",
                "id": screenshot["id"],
                "attributes": {"uploaded": True, "sourceFileChecksum": checksum},
            }
        },
    )
    if response.status_code != 200:
        raise RuntimeError(f"Commit screenshot failed: {response.status_code} {response.text[:500]}")
    print(f"  uploaded {os.path.basename(path)}")


def main():
    screenshot_dir = sys.argv[1] if len(sys.argv) > 1 else "screenshots"
    version = list_all(f"/apps/{APP_ID}/appStoreVersions?filter[platform]=IOS&limit=1")[0]
    print(f"Version {version['id']} state={version['attributes'].get('appStoreState')}")
    localizations = list_all(f"/appStoreVersions/{version['id']}/appStoreVersionLocalizations?limit=20")
    for localization in localizations:
        print(f"Processing locale: {localization['attributes']['locale']}")
        for display_type, filenames in SCREENSHOT_SETS.items():
            paths = [os.path.join(screenshot_dir, name) for name in filenames]
            missing = [path for path in paths if not os.path.exists(path)]
            if missing:
                raise RuntimeError(f"Missing screenshots for {display_type}: {missing}")
            print(f" {display_type}")
            set_id = get_or_create_set(localization["id"], display_type)
            clear_set(set_id)
            for path in paths:
                upload_screenshot(set_id, path)
    print("Done!")


if __name__ == "__main__":
    main()
