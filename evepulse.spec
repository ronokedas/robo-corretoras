# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path
import sys

datas = [("assets", "assets")]
hiddenimports = collect_submodules("keyring.backends") + ["nacl.bindings"]
runtime_dlls = Path(sys.base_prefix) / "DLLs"
binaries = [
    (str(runtime_dlls / "libssl-3-x64.dll"), "."),
    (str(runtime_dlls / "libcrypto-3-x64.dll"), "."),
]

a = Analysis(
    ["evepulse_app.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.QtMultimedia", "PySide6.QtWebEngineCore"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EvePulseTrader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/evepulse.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="EvePulseTrader",
)
