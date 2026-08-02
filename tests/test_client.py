from __future__ import annotations

import unittest
from urllib.parse import parse_qs, urlparse

from evemexapi import AuthenticationError, EvemexClient


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict, dict | None]] = []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append((method, url, headers, body))
        path = urlparse(url).path
        if path == "/auth/login":
            if body["password"] == "bad":
                return {"ok": False, "code": "invalid", "message": "inválido"}
            return {"ok": True, "token": "token-de-teste-comprido"}
        if path == "/me":
            return {
                "accounts": [
                    {"accountId": "d", "tradeId": 1, "type": "DEMO", "balance": 10000},
                    {"accountId": "r", "tradeId": 2, "type": "REAL", "balance": 50},
                ]
            }
        if path == "/otc/assets":
            return {"assets": ["EURUSD_otc"], "timeframes": ["1m"]}
        if path == "/otc/assets/info":
            return {"assets": [{"symbol": "EURUSD_otc", "name": "EURUSD"}]}
        if path == "/otc/candles/latest":
            return {
                "candles": [
                    {"symbol": "EURUSD_otc", "from": 60, "to": 120, "open": 1, "high": 2, "low": 1, "close": 2}
                ]
            }
        if path == "/otc/candles/latest/batch":
            return {
                "results": {
                    "EURUSD_otc": {
                        "candles": [
                            {"from": 60, "to": 120, "open": 1, "high": 2, "low": 1, "close": 2}
                        ]
                    }
                }
            }
        if path == "/ops/expirations":
            return {
                "serverTimeMs": 119000,
                "slots": [{"label": "1M", "expirationAtSec": 180}],
            }
        if path == "/ops/open_operation":
            return {"result": {"id": "op-1"}}
        if path == "/ops/operations/history":
            return {"items": [{"id": "op-1", "status": "closed", "result": "WIN", "profit": 1.98}]}
        if path == "/ops/operations/open":
            return {"items": []}
        raise AssertionError(f"Endpoint inesperado: {path}")


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.client = EvemexClient("user@example.com", "secret", transport=self.transport)
        self.client.connect()

    def test_auth_and_account_selection(self):
        account = self.client.select_account("DEMO")
        self.assertEqual(account.balance, 10000)
        self.assertEqual(account.mode, "DEMO")
        me_call = next(call for call in self.transport.calls if urlparse(call[1]).path == "/me")
        self.assertEqual(me_call[2]["Authorization"], "Bearer token-de-teste-comprido")

    def test_failed_login_does_not_connect(self):
        client = EvemexClient("user@example.com", "bad", transport=self.transport)
        with self.assertRaises(AuthenticationError):
            client.connect()
        self.assertFalse(client.connected)

    def test_assets_candles_and_batch_are_normalized(self):
        self.assertEqual(self.client.get_otc_assets()[0]["symbol"], "EURUSD_otc")
        candle = self.client.get_candles("EURUSD_otc", limit=1)[0]
        self.assertEqual(candle.from_ts, 60)
        batch = self.client.get_candles_batch(["EURUSD_otc"])
        self.assertEqual(batch["EURUSD_otc"][0].symbol, "EURUSD_otc")

    def test_expiration_and_open_payload(self):
        self.client.select_account("DEMO")
        expiration, _ = self.client.select_one_minute_expiration("EURUSD_otc")
        response = self.client.open_operation(
            "EURUSD_otc", 2.0, "DOWN", expiration, client_request_id="req-fixed"
        )
        self.assertEqual(response["result"]["id"], "op-1")
        open_call = next(call for call in self.transport.calls if urlparse(call[1]).path == "/ops/open_operation")
        body = open_call[3]
        self.assertTrue(body["demo"])
        self.assertEqual(body["trend"], "DOWN")
        self.assertEqual(body["expirationAtSec"], 180)
        self.assertEqual(body["clientRequestId"], "req-fixed")

    def test_history_uses_selected_account(self):
        self.client.select_account("REAL")
        result = self.client.wait_result("op-1", timeout=1)
        self.assertEqual(result.result, "WIN")
        history_call = next(call for call in self.transport.calls if urlparse(call[1]).path == "/ops/operations/history")
        self.assertEqual(parse_qs(urlparse(history_call[1]).query)["accountKind"], ["real"])


if __name__ == "__main__":
    unittest.main()
