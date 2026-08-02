import sys

from evepulse_desktop.main import main


def auth_smoke_test() -> int:
    """Diagnóstico somente leitura usado para validar o pacote Windows."""
    try:
        import json
        import traceback
        from evemexapi import EvemexClient
        from evepulse_desktop.config import data_dir
        from evepulse_desktop.google_auth import cdp_storage_token, ready_endpoint

        endpoint = ready_endpoint(data_dir() / "BrowserProfile")
        if endpoint is None:
            return 2
        token = cdp_storage_token(endpoint)
        if not token:
            return 3
        client = EvemexClient()
        client.connect_with_token(token)
        return 0 if client.get_accounts(refresh=False) else 4
    except Exception as exc:
        try:
            diagnostic = data_dir() / "auth-smoke-error.json"
            diagnostic.write_text(json.dumps({
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return 5


if __name__ == "__main__":
    if "--auth-smoke-test" in sys.argv:
        raise SystemExit(auth_smoke_test())
    raise SystemExit(main())
