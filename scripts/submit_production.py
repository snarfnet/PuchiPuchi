import hashlib
import json
import os
import time

import jwt
import requests

KEY_ID = os.environ.get("ASC_KEY_ID", "WDXGY9WX55")
ISSUER = os.environ.get("ASC_ISSUER_ID", "2be0734f-943a-4d61-9dc9-5d9045c46fec")
BUNDLE_ID = os.environ["APP_BUNDLE_ID"]
APP_VERSION = os.environ.get("APP_VERSION", "1.0")
BUILD_NUMBER = os.environ["BUILD_NUMBER"]
P8_PATH = os.environ.get("ASC_P8_PATH", "/tmp/asc_key.p8")
SCREENSHOT_DIR = "MarketingAssets/Screenshots"
PRIVACY_URL = "https://snarfnet.github.io/app-support/"
REVIEW_CONTACT = {
    "contactFirstName": "Tokyo",
    "contactLastName": "Nasu",
    "contactEmail": "tokyonasu@yahoo.co.jp",
    "contactPhone": "+81 80-2368-9194",
}
SCREENSHOT_GROUPS = [
    ("APP_IPHONE_67", "iphone67", 3),
    ("APP_IPHONE_65", "iphone65", 3),
    ("APP_IPHONE_55", "iphone55", 3),
]
AGE_RATING_ATTRIBUTES = {
    "alcoholTobaccoOrDrugUseOrReferences": "NONE",
    "contests": "NONE",
    "gambling": False,
    "gamblingSimulated": "NONE",
    "horrorOrFearThemes": "NONE",
    "matureOrSuggestiveThemes": "NONE",
    "medicalOrTreatmentInformation": "NONE",
    "profanityOrCrudeHumor": "NONE",
    "sexualContentGraphicAndNudity": "NONE",
    "sexualContentOrNudity": "NONE",
    "violenceCartoonOrFantasy": "NONE",
    "violenceRealistic": "NONE",
    "violenceRealisticProlongedGraphicOrSadistic": "NONE",
    "gunsOrOtherWeapons": "NONE",
    "ageRatingOverride": None,
    "advertising": True,
    "ageAssurance": False,
    "healthOrWellnessTopics": False,
    "lootBox": False,
    "messagingAndChat": False,
    "parentalControls": False,
    "unrestrictedWebAccess": False,
    "userGeneratedContent": False,
}

METADATA = json.loads(r'''
{
    "com.tokyonasu.miminenrei": {
        "name": "\u307f\u307f\u5e74\u9f62",
        "category": "HEALTH_AND_FITNESS",
        "description": "\u8033\u306e\u5e74\u9f62\u3092\u304b\u3093\u305f\u3093\u30c1\u30a7\u30c3\u30af\u3002\n\n8,000Hz\u304b\u308918,000Hz\u307e\u3067\u306e\u9ad8\u5468\u6ce2\u97f3\u3092\u9806\u756a\u306b\u518d\u751f\u3057\u3001\u805e\u3053\u3048\u305f\u97f3\u3092\u8a18\u9332\u3057\u307e\u3059\u3002\u7d50\u679c\u306f\u8033\u5e74\u9f62\u306e\u76ee\u5b89\u3068\u3057\u3066\u8868\u793a\u3002\u5404\u5468\u6ce2\u6570\u306e\u805e\u3053\u3048\u65b9\u3082\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002\n\n\u30a4\u30e4\u30db\u30f3\u63a8\u5968\u3002\u9759\u304b\u306a\u5834\u6240\u3067\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002",
        "keywords": "\u8033\u5e74\u9f62,\u8074\u529b,\u8033,\u30c6\u30b9\u30c8,\u9ad8\u5468\u6ce2,Hz,\u805e\u3053\u3048,\u30c1\u30a7\u30c3\u30af,\u5065\u5eb7,\u97f3",
        "promotionalText": "\u3042\u306a\u305f\u306e\u8033\u306f\u4f55\u6b73\uff1f\u9ad8\u5468\u6ce2\u97f3\u3067\u8033\u5e74\u9f62\u3092\u30c1\u30a7\u30c3\u30af\u3002",
        "reviewNotes": "This app plays high-frequency tones and shows an estimated hearing age. No login is required."
    },
    "com.tokyonasu.shinreispot": {
        "name": "\u5fc3\u970a\u30ec\u30fc\u30c0\u30fc",
        "category": "ENTERTAINMENT",
        "description": "\u96f0\u56f2\u6c17\u3092\u697d\u3057\u3080\u5fc3\u970a\u30ec\u30fc\u30c0\u30fc\u30a2\u30d7\u30ea\u3067\u3059\u3002\n\n\u753b\u9762\u3092\u958b\u304f\u3068\u30ec\u30fc\u30c0\u30fc\u304c\u53cd\u5fdc\u3057\u3001\u5468\u56f2\u306e\u6c17\u914d\u3092\u6f14\u51fa\u3057\u307e\u3059\u3002\u6697\u3044\u90e8\u5c4b\u3001\u6563\u6b69\u3001\u53cb\u9054\u3068\u306e\u904a\u3073\u306b\u3074\u3063\u305f\u308a\u3002\u7d50\u679c\u306f\u30a8\u30f3\u30bf\u30e1\u7528\u3067\u3001\u6016\u3055\u3092\u8efd\u304f\u697d\u3057\u3081\u308b\u4f5c\u308a\u3067\u3059\u3002",
        "keywords": "\u5fc3\u970a,\u30ec\u30fc\u30c0\u30fc,\u5e7d\u970a,\u6016\u3044,\u30db\u30e9\u30fc,\u602a\u8ac7,\u6c17\u914d,\u63a2\u77e5,\u30a8\u30f3\u30bf\u30e1,\u904a\u3073",
        "promotionalText": "\u305d\u306e\u5834\u306e\u6c17\u914d\u3092\u30ec\u30fc\u30c0\u30fc\u3067\u30c1\u30a7\u30c3\u30af\u3002\u6016\u3055\u3092\u8efd\u304f\u697d\u3057\u3081\u307e\u3059\u3002",
        "reviewNotes": "Entertainment app. It simulates a ghost radar effect and does not claim real detection. No login is required."
    },
    "com.tokyonasu.metalrate": {
        "name": "\u3072\u3068\u76ee\u3067\u91d1\u5c5e\u76f8\u5834",
        "category": "FINANCE",
        "description": "\u91d1\u30fb\u9280\u30fb\u30d7\u30e9\u30c1\u30ca\u306a\u3069\u306e\u91d1\u5c5e\u76f8\u5834\u3092\u3072\u3068\u76ee\u3067\u898b\u3089\u308c\u308b\u30a2\u30d7\u30ea\u3067\u3059\u3002\n\n\u4e3b\u8981\u306a\u91d1\u5c5e\u4fa1\u683c\u3092\u898b\u3084\u3059\u304f\u4e26\u3079\u3001\u524d\u56de\u6bd4\u306e\u52d5\u304d\u3082\u3059\u3070\u3084\u304f\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002\u8cb7\u53d6\u524d\u306e\u76ee\u5b89\u30c1\u30a7\u30c3\u30af\u3001\u76f8\u5834\u306e\u89b3\u5bdf\u3001\u8cc7\u7523\u30e1\u30e2\u306b\u4fbf\u5229\u3067\u3059\u3002",
        "keywords": "\u91d1\u5c5e\u76f8\u5834,\u91d1,\u9280,\u30d7\u30e9\u30c1\u30ca,\u8cb7\u53d6,\u76f8\u5834,\u4fa1\u683c,\u8cc7\u7523,\u5730\u91d1,\u30de\u30fc\u30b1\u30c3\u30c8",
        "promotionalText": "\u91d1\u30fb\u9280\u30fb\u30d7\u30e9\u30c1\u30ca\u306e\u76f8\u5834\u3092\u3059\u3070\u3084\u304f\u78ba\u8a8d\u3002",
        "reviewNotes": "Finance utility for viewing metal price information. No trading or login is provided."
    },
    "com.tokyonasu.jidouhanbaigacha": {
        "name": "\u81ea\u8ca9\u6a5f\u30ac\u30c1\u30e3",
        "category": "GAMES",
        "description": "\u81ea\u8ca9\u6a5f\u3067\u4f55\u304c\u51fa\u308b\u304b\u3092\u697d\u3057\u3080\u3001\u8efd\u3044\u30ac\u30c1\u30e3\u30a2\u30d7\u30ea\u3067\u3059\u3002\n\n\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068\u7f36\u3084\u30dc\u30c8\u30eb\u304c\u51fa\u73fe\u3002\u30ec\u30a2\u306a\u30c9\u30ea\u30f3\u30af\u3092\u96c6\u3081\u306a\u304c\u3089\u3001\u77ed\u3044\u7a7a\u304d\u6642\u9593\u306b\u904a\u3079\u307e\u3059\u3002\u30b7\u30f3\u30d7\u30eb\u64cd\u4f5c\u3067\u3001\u5b50\u3069\u3082\u304b\u3089\u5927\u4eba\u307e\u3067\u697d\u3057\u3081\u308b\u5185\u5bb9\u3067\u3059\u3002",
        "keywords": "\u81ea\u8ca9\u6a5f,\u30ac\u30c1\u30e3,\u30b2\u30fc\u30e0,\u30c9\u30ea\u30f3\u30af,\u7f36,\u30b3\u30ec\u30af\u30b7\u30e7\u30f3,\u304f\u3058,\u6687\u3064\u3076\u3057,\u7121\u6599,\u30ab\u30b8\u30e5\u30a2\u30eb",
        "promotionalText": "\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3060\u3051\u3002\u4eca\u65e5\u306f\u3069\u306e\u30c9\u30ea\u30f3\u30af\u304c\u51fa\u308b\uff1f",
        "reviewNotes": "Casual vending machine gacha game. No real-money purchase, gambling, or login is required."
    },
    "com.tokyonasu.puchipuchi": {
        "name": "\u30d7\u30c1\u30d7\u30c1\u7121\u9650",
        "category": "ENTERTAINMENT",
        "description": "\u7121\u9650\u306b\u30d7\u30c1\u30d7\u30c1\u3067\u304d\u308b\u30ea\u30e9\u30c3\u30af\u30b9\u30a2\u30d7\u30ea\u3067\u3059\u3002\n\n\u753b\u9762\u306e\u7c92\u3092\u30bf\u30c3\u30d7\u3057\u3066\u3001\u6c17\u6301\u3061\u3044\u3044\u97f3\u3068\u53cd\u5fdc\u3092\u697d\u3057\u3081\u307e\u3059\u3002\u5c11\u3057\u4f11\u307f\u305f\u3044\u6642\u3001\u96c6\u4e2d\u306e\u5408\u9593\u3001\u306a\u3093\u3068\u306a\u304f\u624b\u3092\u52d5\u304b\u3057\u305f\u3044\u6642\u306b\u3069\u3046\u305e\u3002",
        "keywords": "\u30d7\u30c1\u30d7\u30c1,\u7121\u9650,\u6687\u3064\u3076\u3057,\u30ea\u30e9\u30c3\u30af\u30b9,\u30b9\u30c8\u30ec\u30b9\u89e3\u6d88,\u30bf\u30c3\u30d7,\u97f3,\u7652\u3057,\u904a\u3073,\u30b7\u30f3\u30d7\u30eb",
        "promotionalText": "\u3044\u3064\u3067\u3082\u3069\u3053\u3067\u3082\u3001\u7121\u9650\u306b\u30d7\u30c1\u30d7\u30c1\u3002",
        "reviewNotes": "Simple relaxation app for popping bubbles. No login is required."
    }
}
''')

p8 = open(P8_PATH, encoding="utf-8").read()


def token():
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"}, p8, algorithm="ES256", headers={"kid": KEY_ID})


def headers():
    return {"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}


def api(method, path, **kwargs):
    for _ in range(6):
        response = requests.request(method, f"https://api.appstoreconnect.apple.com/v1{path}", headers=headers(), timeout=120, **kwargs)
        if response.status_code not in (401, 429, 500, 502, 503, 504):
            return response
        time.sleep(20)
    return response


def api_json(method, path, **kwargs):
    response = api(method, path, **kwargs)
    try:
        return response, response.json()
    except Exception:
        return response, {}


def error_text(response, limit=3000):
    try:
        return json.dumps(response.json(), ensure_ascii=False)[:limit]
    except Exception:
        return response.text[:limit]


def list_all(path):
    rows = []
    next_path = path
    while next_path:
        response, body = api_json("GET", next_path)
        if response.status_code != 200:
            raise RuntimeError(f"List failed {response.status_code}: {response.text[:800]}")
        rows.extend(body.get("data", []))
        next_url = body.get("links", {}).get("next")
        next_path = next_url.split("/v1", 1)[1] if next_url else None
    return rows


def app_meta():
    if BUNDLE_ID not in METADATA:
        raise RuntimeError(f"Missing metadata for {BUNDLE_ID}")
    return METADATA[BUNDLE_ID]


def find_app_id():
    response, body = api_json("GET", f"/apps?filter[bundleId]={BUNDLE_ID}&limit=1")
    if response.status_code != 200 or not body.get("data"):
        raise RuntimeError(f"App not found for {BUNDLE_ID}: {response.text[:500]}")
    return body["data"][0]["id"]


def find_or_create_version(app_id):
    for version in list_all(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=200"):
        attrs = version.get("attributes", {})
        if attrs.get("versionString") == APP_VERSION:
            return version["id"], attrs.get("appStoreState")
    payload = {"data": {"type": "appStoreVersions", "attributes": {"platform": "IOS", "versionString": APP_VERSION}, "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}}
    response, body = api_json("POST", "/appStoreVersions", json=payload)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Version create failed {response.status_code}: {response.text[:800]}")
    return body["data"]["id"], "PREPARE_FOR_SUBMISSION"


def wait_for_build(app_id):
    for i in range(90):
        response, body = api_json("GET", f"/builds?filter[app]={app_id}&filter[version]={BUILD_NUMBER}&filter[processingState]=VALID&limit=1")
        if body.get("data"):
            return body["data"][0]["id"]
        print(f"Waiting for build {BUILD_NUMBER} processing... {i + 1}/90")
        time.sleep(30)
    raise RuntimeError(f"Build {BUILD_NUMBER} did not finish processing")


def ensure_app_info(app_id):
    meta = app_meta()
    response = api("PATCH", f"/apps/{app_id}", json={"data": {"type": "apps", "id": app_id, "attributes": {"contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT"}}})
    print(f"Content rights: {response.status_code}")

    infos = list_all(f"/apps/{app_id}/appInfos?limit=10")
    if not infos:
        raise RuntimeError("appInfo not found")
    app_info_id = infos[0]["id"]
    category_payload = {"data": {"type": "appInfos", "id": app_info_id, "relationships": {"primaryCategory": {"data": {"type": "appCategories", "id": meta["category"]}}}}}
    response = api("PATCH", f"/appInfos/{app_info_id}", json=category_payload)
    print(f"Category: {response.status_code}")

    locs = list_all(f"/appInfos/{app_info_id}/appInfoLocalizations?limit=50")
    ja = next((loc for loc in locs if loc["attributes"].get("locale") == "ja"), None)
    payload = {"data": {"type": "appInfoLocalizations", "attributes": {"locale": "ja", "name": meta["name"]}, "relationships": {"appInfo": {"data": {"type": "appInfos", "id": app_info_id}}}}}
    if ja:
        payload = {"data": {"type": "appInfoLocalizations", "id": ja["id"], "attributes": {"name": meta["name"], "privacyPolicyUrl": PRIVACY_URL}}}
        response = api("PATCH", f"/appInfoLocalizations/{ja['id']}", json=payload)
    else:
        payload["data"]["attributes"]["privacyPolicyUrl"] = PRIVACY_URL
        response = api("POST", "/appInfoLocalizations", json=payload)
    print(f"App name: {response.status_code}")
    return app_info_id


def update_age_rating(app_info_id):
    response, body = api_json("GET", f"/appInfos/{app_info_id}/ageRatingDeclaration")
    if response.status_code != 200 or not body.get("data"):
        print(f"Age rating lookup: {response.status_code} {error_text(response, 800)}")
        return
    rating_id = body["data"]["id"]
    payload = {"data": {"type": "ageRatingDeclarations", "id": rating_id, "attributes": AGE_RATING_ATTRIBUTES}}
    response = api("PATCH", f"/ageRatingDeclarations/{rating_id}", json=payload)
    print(f"Age rating: {response.status_code}")


def update_version_settings(version_id):
    attrs = {"copyright": "2026 tokyonasu", "releaseType": "MANUAL"}
    response = api("PATCH", f"/appStoreVersions/{version_id}", json={"data": {"type": "appStoreVersions", "id": version_id, "attributes": attrs}})
    print(f"Version settings: {response.status_code}")


def ensure_localization(version_id):
    localizations = list_all(f"/appStoreVersions/{version_id}/appStoreVersionLocalizations?limit=200")
    ja = next((item for item in localizations if item["attributes"].get("locale") == "ja"), None)
    if ja:
        return ja
    payload = {"data": {"type": "appStoreVersionLocalizations", "attributes": {"locale": "ja"}, "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}}
    response, body = api_json("POST", "/appStoreVersionLocalizations", json=payload)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Localization create failed {response.status_code}: {response.text[:800]}")
    return body["data"]


def update_metadata(version_id):
    loc = ensure_localization(version_id)
    meta = app_meta()
    attrs = {
        "description": meta["description"],
        "keywords": meta["keywords"],
        "promotionalText": meta["promotionalText"],
        "supportUrl": "https://snarfnet.github.io/app-support/",
        "marketingUrl": "https://snarfnet.github.io/app-support/",
    }
    response = api("PATCH", f"/appStoreVersionLocalizations/{loc['id']}", json={"data": {"type": "appStoreVersionLocalizations", "id": loc["id"], "attributes": attrs}})
    print(f"Metadata: {response.status_code}")
    if response.status_code >= 400:
        print(error_text(response, 1200))


def update_review_detail(version_id):
    meta = app_meta()
    attrs = {**REVIEW_CONTACT, "demoAccountRequired": False, "demoAccountName": "", "demoAccountPassword": "", "notes": meta["reviewNotes"]}
    response, body = api_json("GET", f"/appStoreVersions/{version_id}/appStoreReviewDetail")
    if response.status_code == 200 and body.get("data"):
        detail_id = body["data"]["id"]
        response = api("PATCH", f"/appStoreReviewDetails/{detail_id}", json={"data": {"type": "appStoreReviewDetails", "id": detail_id, "attributes": attrs}})
    else:
        response = api("POST", "/appStoreReviewDetails", json={"data": {"type": "appStoreReviewDetails", "attributes": attrs, "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}})
    print(f"Review detail: {response.status_code}")


def upload_screenshots(version_id):
    loc = ensure_localization(version_id)
    sets = list_all(f"/appStoreVersionLocalizations/{loc['id']}/appScreenshotSets?limit=200")
    existing = {item["attributes"]["screenshotDisplayType"]: item["id"] for item in sets}
    for display_type, prefix, count in SCREENSHOT_GROUPS:
        set_id = existing.get(display_type)
        if not set_id:
            payload = {"data": {"type": "appScreenshotSets", "attributes": {"screenshotDisplayType": display_type}, "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": loc["id"]}}}}}
            response, body = api_json("POST", "/appScreenshotSets", json=payload)
            if response.status_code not in (200, 201):
                print(f"Screenshot set {display_type}: {response.status_code} {response.text[:500]}")
                continue
            set_id = body["data"]["id"]
        for screenshot in list_all(f"/appScreenshotSets/{set_id}/appScreenshots?limit=200"):
            api("DELETE", f"/appScreenshots/{screenshot['id']}")
        for i in range(1, count + 1):
            upload_screenshot(set_id, f"{prefix}/{prefix}_{i:02d}.png")


def upload_screenshot(set_id, rel_path):
    path = os.path.join(SCREENSHOT_DIR, rel_path)
    if not os.path.exists(path):
        print(f"Missing screenshot: {path}")
        return
    data = open(path, "rb").read()
    checksum = hashlib.md5(data).hexdigest()
    filename = os.path.basename(rel_path)
    payload = {"data": {"type": "appScreenshots", "attributes": {"fileName": filename, "fileSize": len(data)}, "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}}}}
    response, body = api_json("POST", "/appScreenshots", json=payload)
    if response.status_code not in (200, 201):
        print(f"Screenshot create failed {rel_path}: {response.status_code} {response.text[:500]}")
        return
    screenshot_id = body["data"]["id"]
    for op in body["data"]["attributes"]["uploadOperations"]:
        headers_for_upload = {item["name"]: item["value"] for item in op["requestHeaders"]}
        chunk = data[op["offset"]:op["offset"] + op["length"]]
        requests.put(op["url"], headers=headers_for_upload, data=chunk, timeout=120).raise_for_status()
    response = api("PATCH", f"/appScreenshots/{screenshot_id}", json={"data": {"type": "appScreenshots", "id": screenshot_id, "attributes": {"uploaded": True, "sourceFileChecksum": checksum}}})
    print(f"Screenshot {rel_path}: {response.status_code}")


def assign_build(version_id, build_id):
    response = api("PATCH", f"/builds/{build_id}", json={"data": {"type": "builds", "id": build_id, "attributes": {"usesNonExemptEncryption": False}}})
    print(f"Encryption: {response.status_code}")
    response = api("PATCH", f"/appStoreVersions/{version_id}/relationships/build", json={"data": {"type": "builds", "id": build_id}})
    print(f"Assign build: {response.status_code}")


def submit_for_review(app_id, version_id):
    cancel_pending_review_submissions(app_id)

    legacy_payload = {"data": {"type": "appStoreVersionSubmissions", "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}}
    response, body = api_json("POST", "/appStoreVersionSubmissions", json=legacy_payload)
    if response.status_code in (200, 201):
        print("Submitted via appStoreVersionSubmissions")
        return
    print(f"Legacy submit: {response.status_code} {error_text(response, 1200)}")

    payload = {"data": {"type": "reviewSubmissions", "attributes": {"platform": "IOS"}, "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}}
    response, body = api_json("POST", "/reviewSubmissions", json=payload)
    if response.status_code != 201:
        raise RuntimeError(f"Review submission create failed {response.status_code}: {error_text(response)}")
    submission_id = body["data"]["id"]
    item_ok = False
    for _ in range(20):
        response = api("POST", "/reviewSubmissionItems", json={"data": {"type": "reviewSubmissionItems", "relationships": {"reviewSubmission": {"data": {"type": "reviewSubmissions", "id": submission_id}}, "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}})
        if response.status_code == 201:
            item_ok = True
            break
        print(f"Review item: {response.status_code} {error_text(response, 1200)}")
        time.sleep(30)
    if not item_ok:
        raise RuntimeError("Review submission item was not accepted")
    response, body = api_json("PATCH", f"/reviewSubmissions/{submission_id}", json={"data": {"type": "reviewSubmissions", "id": submission_id, "attributes": {"submitted": True}}})
    if response.status_code != 200:
        raise RuntimeError(f"Submit failed {response.status_code}: {error_text(response)}")
    print(f"Submitted: {body['data']['attributes']['state']}")


def cancel_pending_review_submissions(app_id):
    response, body = api_json("GET", f"/apps/{app_id}/reviewSubmissions?limit=50")
    if response.status_code != 200:
        print(f"Review submission lookup: {response.status_code} {error_text(response, 800)}")
        return
    for submission in body.get("data", []):
        state = submission.get("attributes", {}).get("state")
        if state not in ("READY_FOR_REVIEW", "WAITING_FOR_REVIEW"):
            continue
        submission_id = submission["id"]
        response = api("PATCH", f"/reviewSubmissions/{submission_id}", json={"data": {"type": "reviewSubmissions", "id": submission_id, "attributes": {"canceled": True}}})
        print(f"Cancel review submission {submission_id}: {response.status_code}")


def main():
    app_id = find_app_id()
    app_info_id = ensure_app_info(app_id)
    update_age_rating(app_info_id)
    version_id, state = find_or_create_version(app_id)
    if state in ("WAITING_FOR_REVIEW", "IN_REVIEW"):
        print(f"Already submitted: {state}")
        return
    update_version_settings(version_id)
    update_metadata(version_id)
    update_review_detail(version_id)
    upload_screenshots(version_id)
    print("Waiting for build processing and screenshots...")
    build_id = wait_for_build(app_id)
    time.sleep(300)
    assign_build(version_id, build_id)
    submit_for_review(app_id, version_id)


if __name__ == "__main__":
    main()
