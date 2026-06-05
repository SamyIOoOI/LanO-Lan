# -*- mode: python ; coding: utf-8 -*-
a_main = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),       
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

a_register = Analysis(
    ['register.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('2fixed32px.png', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

all_binaries = a_main.binaries + a_register.binaries
all_datas = a_main.datas + a_register.datas

pyz_main = PYZ(a_main.pure)
pyz_register = PYZ(a_register.pure)
exe_main = EXE(
    pyz_main,
    a_main.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,     
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
exe_register = EXE(
    pyz_register,
    a_register.scripts,
    [],
    exclude_binaries=True,
    name='register',
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
    icon='icon.ico',
)
coll = COLLECT(
    exe_main,
    exe_register,
    all_binaries,
    all_datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LanO_Lan',
)