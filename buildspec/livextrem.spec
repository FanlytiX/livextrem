# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = [('C:\\Users\\Marc\\Desktop\\Projektarbeit\\livextrem\\livextrem\\config_local.json', '_internal'), ('C:\\Users\\Marc\\Desktop\\Projektarbeit\\livextrem\\livextrem\\images\\logo.png', '_internal\\images'), ('C:\\Users\\Marc\\Desktop\\Projektarbeit\\livextrem\\livextrem\\images\\logo.png', '_internal\\livextrem\\images'), ('C:\\Users\\Marc\\Desktop\\Projektarbeit\\livextrem\\livextrem\\style.json', '_internal'), ('C:\\Users\\Marc\\Desktop\\Projektarbeit\\livextrem\\livextrem\\style.json', '_internal\\livextrem')]
hiddenimports = ['certifi', 'mysql.connector.locales.eng', 'mysql.connector.locales.eng.client_error']
datas += collect_data_files('certifi')
datas += collect_data_files('mysql.connector')
hiddenimports += collect_submodules('mysql.connector')


a = Analysis(
    ['..\\livextrem\\login.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='livextrem',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='livextrem',
)
