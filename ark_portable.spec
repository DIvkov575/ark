# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

current_dir = Path.cwd()

a = Analysis(
    ['launcher.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        ('templates/', 'templates'),
        ('api/configs/', 'api/configs'),
        ('static/', 'static'),
        ('version.py', '.'),
        ('main.py', '.'),
        ('launcher.py', '.'),
        ('api', 'api'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'flask',
        'werkzeug',
        'jinja2',
        'pydicom',
        'requests',
        'PIL',
        'numpy',
        'json',
        'io',
        'tempfile',
        'threading',
        'multiprocessing',
        'signal',
        'subprocess',
        'webbrowser',
        'api.app',
        'api.config',
        'api.logging_utils',
        'api.storage',
        'api.utils',
        'models.base',
        'models.mirai',
        'models.sybil',
        'models.density',
        'models.utils',
        'onconet',
        'sybil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ark_portable',
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
    icon=None,
)