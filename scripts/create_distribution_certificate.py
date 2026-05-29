#!/usr/bin/env python3
import base64
import hashlib
import os
import subprocess
from pathlib import Path

from asc_helpers import api_json, fail, json_body

KEYCHAIN = os.environ.get("BUILD_KEYCHAIN", "build.keychain")
WORK_DIR = Path("/tmp/puchipuchi-signing")
KEY_PATH = WORK_DIR / "distribution.key"
CSR_PATH = WORK_DIR / "distribution.csr"
CERT_PATH = WORK_DIR / "distribution.cer"


def run(args):
    print("+", " ".join(str(arg) for arg in args), flush=True)
    subprocess.run(args, check=True)


def export_env(name, value):
    print(f"{name}={value}")
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as file:
            file.write(f"{name}={value}\n")


def generate_csr():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    run(["openssl", "genrsa", "-out", str(KEY_PATH), "2048"])
    run([
        "openssl",
        "req",
        "-new",
        "-key",
        str(KEY_PATH),
        "-out",
        str(CSR_PATH),
        "-subj",
        "/CN=PuchiPuchi CI Distribution/O=TokyoNasu/C=JP",
    ])


def create_certificate():
    csr_content = CSR_PATH.read_text(encoding="utf-8")
    last_error = None
    for certificate_type in ("DISTRIBUTION", "IOS_DISTRIBUTION"):
        payload = {
            "data": {
                "type": "certificates",
                "attributes": {
                    "certificateType": certificate_type,
                    "csrContent": csr_content,
                },
            }
        }
        try:
            certificate = api_json("POST", "/certificates", data=json_body(payload))["data"]
            print(f"Created certificate: {certificate['id']} ({certificate_type})")
            return certificate
        except Exception as error:
            last_error = error
            print(f"Certificate create failed for {certificate_type}: {error}")
    raise RuntimeError(last_error)


def import_certificate(certificate):
    content = certificate.get("attributes", {}).get("certificateContent")
    if not content:
        raise RuntimeError("Created certificate did not include certificateContent.")

    CERT_PATH.write_bytes(base64.b64decode(content))
    run(["security", "import", str(KEY_PATH), "-k", KEYCHAIN, "-T", "/usr/bin/codesign", "-T", "/usr/bin/security"])
    run(["security", "import", str(CERT_PATH), "-k", KEYCHAIN, "-T", "/usr/bin/codesign", "-T", "/usr/bin/security"])
    run(["security", "set-key-partition-list", "-S", "apple-tool:,apple:", "-s", "-k", os.environ["KEYCHAIN_PASSWORD"], KEYCHAIN])

    sha1 = hashlib.sha1(CERT_PATH.read_bytes()).hexdigest().upper()
    export_env("IOS_DISTRIBUTION_CERT_SHA1", sha1)
    export_env("ASC_CERTIFICATE_ID", certificate["id"])


def main():
    generate_csr()
    certificate = create_certificate()
    import_certificate(certificate)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        fail(error)
