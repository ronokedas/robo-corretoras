import base64
import io
import json
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError

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


def test_license_request_identifies_evepulse(tmp_path, monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'{"ok":true}'

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("evepulse_desktop.licensing.urlopen", fake_urlopen)
    client = LicenseClient("https://example.com/robo", storage_dir=tmp_path)

    assert client._request("/api/test", {"ok": True}) == {"ok": True}
    assert captured["request"].get_header("User-agent").startswith("EvePulseTrader/")
    assert captured["timeout"] == 6


def test_cloudflare_block_has_actionable_message(tmp_path, monkeypatch):
    payload = json.dumps({"error_code": 1010, "detail": "Access denied"}).encode()

    def blocked(*_args, **_kwargs):
        raise HTTPError("https://example.com", 403, "Forbidden", {}, io.BytesIO(payload))

    monkeypatch.setattr("evepulse_desktop.licensing.urlopen", blocked)
    client = LicenseClient("https://example.com/robo", storage_dir=tmp_path)

    try:
        client._request("/api/test", {"ok": True})
    except LicenseError as exc:
        assert exc.status == 403
        assert "proteção do site" in str(exc)
    else:
        raise AssertionError("bloqueio do Cloudflare não foi reportado")
