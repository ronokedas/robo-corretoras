from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

APP_NAME = "EvePulse Trader"
APP_VERSION = "1.0.4"
try:
    from .production_config import LICENSE_PUBLIC_KEY as BUILT_PUBLIC_KEY
    from .production_config import LICENSE_URL as BUILT_LICENSE_URL
except ImportError:
    BUILT_LICENSE_URL = "http://127.0.0.1:8042"
    BUILT_PUBLIC_KEY = "3a_xebWTItecTKUdTVXZUJENd3NofOulkohAv4xmj-I"

LICENSE_URL = os.environ.get("EVEPULSE_LICENSE_URL", BUILT_LICENSE_URL).rstrip("/")
LICENSE_PUBLIC_KEY = os.environ.get("EVEPULSE_LICENSE_PUBLIC_KEY", BUILT_PUBLIC_KEY).strip()


def data_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EvePulseTrader"
    root.mkdir(parents=True, exist_ok=True)
    return root


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / name


class Settings:
    def __init__(self) -> None:
        self.path = data_dir() / "settings.json"
        self.values: dict[str, Any] = {
            "account": "DEMO",
            "amount": 2.0,
            "stop_loss": 0.0,
            "max_operations": 0,
            "dry_run": True,
        }
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.values.update(loaded)
        except (OSError, ValueError):
            pass

    def save(self, **values: Any) -> None:
        self.values.update(values)
        self.path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
