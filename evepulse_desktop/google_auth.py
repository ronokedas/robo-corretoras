from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

import websocket
from PySide6.QtCore import QThread, Signal

from evemexapi import EvemexClient
from .config import data_dir


def find_browser() -> Path | None:
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
    ]
    return next((item for item in candidates if item.is_file()), None)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def endpoint_responds(endpoint: str) -> bool:
    try:
        with urlopen(endpoint + "/json/version", timeout=1) as response:
            json.loads(response.read())
        return True
    except (OSError, ValueError):
        return False


def ready_endpoint(profile: Path) -> str | None:
    candidates: list[int] = []
    for port_file in (profile / "evepulse-debug-port", profile / "DevToolsActivePort"):
        try:
            candidates.append(int(port_file.read_text(encoding="utf-8").splitlines()[0]))
        except (OSError, ValueError, IndexError):
            pass
    if not candidates:
        escaped = str(profile).replace("'", "''")
        script = (
            "$p='" + escaped + "'; "
            "Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('chrome.exe','msedge.exe') -and "
            "$_.CommandLine -like ('*'+$p+'*') -and $_.CommandLine -match '--remote-debugging-port=(\\d+)' } | "
            "ForEach-Object { if ($_.CommandLine -match '--remote-debugging-port=(\\d+)') { $matches[1] } } | Select-Object -First 1"
        )
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True, text=True, timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode == 0 and result.stdout.strip():
                candidates.append(int(result.stdout.strip().splitlines()[0]))
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    for port in dict.fromkeys(candidates):
        endpoint = f"http://127.0.0.1:{port}"
        if endpoint_responds(endpoint):
            (profile / "evepulse-debug-port").write_text(str(port), encoding="utf-8")
            return endpoint
    return None


def cdp_storage_token(endpoint: str) -> str | None:
    """Lê somente o token de sessão pelo protocolo local do Chrome."""
    try:
        with urlopen(endpoint + "/json/list", timeout=2) as response:
            targets = json.loads(response.read())
    except (OSError, ValueError):
        return None
    pages = [
        item for item in targets
        if isinstance(item, dict)
        and item.get("type") == "page"
        and "trade.evemex.com" in str(item.get("url", ""))
    ]
    for page in pages:
        ws_url = page.get("webSocketDebuggerUrl")
        if not isinstance(ws_url, str):
            continue
        connection = None
        try:
            connection = websocket.create_connection(ws_url, timeout=2, suppress_origin=True)
            connection.send(json.dumps({
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "localStorage.getItem('evemex_auth_token')",
                    "returnByValue": True,
                },
            }))
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                message = json.loads(connection.recv())
                if message.get("id") != 1:
                    continue
                value = message.get("result", {}).get("result", {}).get("value")
                if isinstance(value, str) and len(value.strip()) >= 32:
                    return value.removeprefix("Bearer ").strip().strip('"')
                break
        except (OSError, ValueError, websocket.WebSocketException):
            continue
        finally:
            if connection is not None:
                connection.close()
    return None


class GoogleAuthWorker(QThread):
    status = Signal(str)
    authenticated = Signal(str, object)
    failed = Signal(str)

    def run(self) -> None:
        browser_path = find_browser()
        if browser_path is None:
            self.failed.emit("Google Chrome ou Microsoft Edge não foi encontrado.")
            return
        profile = data_dir() / "BrowserProfile"
        profile.mkdir(parents=True, exist_ok=True)
        endpoint = ready_endpoint(profile)
        process = None
        if endpoint is None:
            port = free_port()
            endpoint = f"http://127.0.0.1:{port}"
            process = subprocess.Popen(
                [
                    str(browser_path), f"--remote-debugging-port={port}",
                    "--remote-debugging-address=127.0.0.1", f"--user-data-dir={profile}",
                    "--no-first-run", "--no-default-browser-check", "--disable-background-mode",
                    "https://trade.evemex.com/traderoom",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.status.emit("Navegador aberto — conclua o login Google na Evemex")
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline and not self.isInterruptionRequested():
                if endpoint_responds(endpoint):
                    (profile / "evepulse-debug-port").write_text(str(port), encoding="utf-8")
                    break
                time.sleep(0.25)
            else:
                self.failed.emit("O navegador não respondeu a tempo.")
                return
        else:
            self.status.emit("Sessão do navegador encontrada — confirmando login Evemex…")

        deadline = time.monotonic() + 300
        while time.monotonic() < deadline and not self.isInterruptionRequested():
            token = cdp_storage_token(endpoint)
            if token:
                try:
                    client = EvemexClient()
                    client.connect_with_token(token)
                    accounts = client.get_accounts(refresh=False)
                    summary = [{"mode": account.mode, "balance": account.balance} for account in accounts]
                    self.authenticated.emit(token, summary)
                    self.status.emit("Conta Evemex autenticada com sucesso")
                    return
                except Exception:
                    pass
            time.sleep(0.5)
        if not self.isInterruptionRequested():
            self.failed.emit("Não foi possível reconhecer a sessão Evemex. Saia e entre novamente no navegador aberto.")
        elif process is not None and process.poll() is None:
            process.terminate()
