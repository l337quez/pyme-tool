# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

base_path = os.getcwd()

a = Analysis(
    [os.path.join(base_path, 'main.py')],
    pathex=[base_path],
    binaries=[],
    datas=[
        (os.path.join(base_path, 'assets'), 'assets'),
        (os.path.join(base_path, 'plugins'), 'plugins'),
        (os.path.join(base_path, 'printers'), 'printers'),
    ],
    hiddenimports=[
        'PySide6.QtXml', 
        'PySide6.QtOpenGL',
        'sqlite3',
        'urllib.request',
        'subprocess',
        'webbrowser',
        'zipfile',
        'shutil',
        'plugin_base'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PYME Tool',
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
    icon='assets/app/pyme-tools.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PYME Tool',
)
