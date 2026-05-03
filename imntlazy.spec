# -*- mode: python ; coding: utf-8 -*-

import os

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join('imntlazy', 'resources', 'haarcascade_frontalface_default.xml'),
         os.path.join('imntlazy', 'resources')),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'cv2',
        'numpy',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='imntlazy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='imntlazy.ico',
    uac_admin=True,
)
