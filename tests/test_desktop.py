import base64
import json
from datetime import datetime, timedelta, timezone

from nacl.signing import SigningKey

from evepulse_desktop.licensing import LicenseClient, LicenseError


def encoded(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def test_signed_lease_rejects_tampering(tmp_path, monkeypatch):
    client = LicenseClient("http://127.0.0.1:1", storage_dir=tmp_path)
    signing = SigningKey.generate()
    monkeypatch.setattr("evepulse_desktop.licensing.LICENSE_PUBLIC_KEY", encoded(bytes(signing.verify_key)))
    now = datetime.now(timezone.utc)
    payload = {
        "license_id": 1,
        "device_hash": client.device_hash,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(days=30)).isoformat(),
        "lease_expires_at": (now + timedelta(hours=72)).isoformat(),
        "minimum_version": "1.0.0",
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    response = {"payload": encoded(raw), "signature": encoded(signing.sign(raw).signature)}
    assert client._verify_response(response)["license_id"] == 1
    response["payload"] = encoded(raw + b" ")
    try:
        client._verify_response(response)
    except LicenseError:
        pass
    else:
        raise AssertionError("lease adulterada foi aceita")
