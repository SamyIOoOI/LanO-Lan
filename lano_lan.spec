# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

ttkthemes_datas = collect_data_files("ttkthemes")

a_main = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),       
    ],
    hiddenimports=['websockets', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'websockets.legacy.server', 'websockets.legacy.client'],
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
    ] + ttkthemes_datas,
    hiddenimports=['tkinter', 'ttkthemes'],
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
    name="LoLServer",
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
    icon='server_icon.ico',
)
exe_register = EXE(
    pyz_register,
    a_register.scripts,
    [],
    exclude_binaries=True,
    name="LanO'Lan",
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