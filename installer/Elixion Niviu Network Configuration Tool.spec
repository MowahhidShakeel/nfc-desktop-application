# -*- mode: python ; coding: utf-8 -*-
import sys, os

# Project root is one level up from "installer"
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "")))

from src.version import APP_NAME, APP_VERSION

a = Analysis(
    ['../src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../src/gui/assets', '_internal/assets'),
        ('../resources/elixion_medical.ico', 'resources'),
    ],
    hiddenimports=['PyQt6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f"{APP_NAME} v{APP_VERSION}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../resources/elixion_medical.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f"{APP_NAME}",
)
