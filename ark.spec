# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['ark'],
    binaries=[],
    datas=[
        ('templates/*', 'templates'),
        ('api/configs/*', 'api/configs'),
        ('static/*', 'static'),
        # Include any additional folders/files your app needs (for example, if the model files, etc.)
    ],
    hiddenimports=[
        # list any modules that might be imported at runtime (for example via importlib)
    ],
    hookspath=[],
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
    name='ark',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Use console=False if you prefer a windowed app
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ark'
)
