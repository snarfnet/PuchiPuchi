#!/usr/bin/env python3
import base64
import hashlib
import os
from pathlib import Path

from asc_helpers import api_json, decode_profile, fail

BUNDLE_ID = os.environ.get("APP_BUNDLE_ID", "com.tokyonasu.puchipuchi")
PROFILE_NAME = os.environ.get("PROFILE_NAME", "PuchiPuchi AppStore")
PROFILE_PATH = Path(os.environ.get(
    "PROFILE_PATH",
    str(Path.home() / "Library/MobileDevice/Provisioning Profiles/PuchiPuchi_AppStore.mobileprovision"),
))
CERT_SHA1 = os.environ.get("IOS_DISTRIBUTION_CERT_SHA1", "").replace(":", "").upper()


def cert_sha1(certificate):
    content = certificate.get("attributes", {}).get("certificateContent")
    if not content:
        detail = api_json("GET", f"/certificates/{certificate['id']}").get("data", certificate)
        content = detail.get("attributes", {}).get("certificateContent")
    if not content:
        return ""
    return hashlib.sha1(base64.b64decode(content)).hexdigest().upper()


def find_distribution_certificate():
    certificates = []
    for cert_type in ("IOS_DISTRIBUTION", "DISTRIBUTION"):
        certificates.extend(api_json("GET", f"/certificates?filter[certificateType]={cert_type}&limit=20").get("data", []))
    if CERT_SHA1:
        for certificate in certificates:
            if cert_sha1(certificate) == CERT_SHA1:
                return certificate
    if certificates:
        return certificates[0]
    raise RuntimeError("No distribution certificate found.")


def profile_certificate_ids(profile_id):
    data = api_json("GET", f"/profiles/{profile_id}/relationships/certificates?limit=10").get("data", [])
    return {item["id"] for item in data}


def find_or_create_profile(bundle_id, certificate_id):
    existing = api_json("GET", f"/profiles?filter[name]={PROFILE_NAME}&limit=20").get("data", [])
    for profile in existing:
        attrs = profile.get("attributes", {})
        if certificate_id in profile_certificate_ids(profile["id"]) and attrs.get("profileContent"):
            return profile
        print(f"Deleting stale provisioning profile: {profile['id']} ({attrs.get('profileState', 'unknown')})")
        api_json("DELETE", f"/profiles/{profile['id']}")

    payload = {
        "data": {
            "type": "profiles",
            "attributes": {"name": PROFILE_NAME, "profileType": "IOS_APP_STORE"},
            "relationships": {
                "bundleId": {"data": {"type": "bundleIds", "id": bundle_id}},
                "certificates": {"data": [{"type": "certificates", "id": certificate_id}]},
            },
        }
    }
    return api_json("POST", "/profiles", json=payload)["data"]


def main():
    data = api_json("GET", f"/bundleIds?filter[identifier]={BUNDLE_ID}&limit=1").get("data", [])
    if not data:
        raise RuntimeError(f"Bundle ID does not exist: {BUNDLE_ID}")

    certificate = find_distribution_certificate()
    profile = find_or_create_profile(data[0]["id"], certificate["id"])
    content = profile.get("attributes", {}).get("profileContent")
    if not content:
        profile = api_json("GET", f"/profiles/{profile['id']}")["data"]
        content = profile.get("attributes", {}).get("profileContent")
    if not content:
        raise RuntimeError("Provisioning profile was created, but profileContent was empty.")

    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_bytes(decode_profile(content))
    print(PROFILE_PATH)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        fail(error)
