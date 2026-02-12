# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec-Datei für OpenClaw GUI.
Erstellt eine standalone EXE mit eingebetteten Templates, Static-Files und Icon.
"""

import os

block_cipher = None
base_dir = os.path.abspath(os.path.dirname(SPEC))

a = Analysis(
    [os.path.join(base_dir, 'app.py')],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'templates'), 'templates'),
        (os.path.join(base_dir, 'static'), 'static'),
    ],
    hiddenimports=[
        'flask',
        'jinja2',
        'markupsafe',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.debug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'pydoc',
        'doctest',
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OpenClaw-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(base_dir, 'static', 'openclaw.ico'),
)
