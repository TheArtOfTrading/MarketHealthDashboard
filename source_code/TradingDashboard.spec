# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['trading_dashboard_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['market_health_dashboard', 'us_sector_dashboard', 'asx_sector_dashboard', 'global_indexes_monthly', 'momentum_stocks', 'forex_dashboard', 'norgatedata', 'logbook', 'matplotlib.backends.backend_tkagg'],
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
    name='TradingDashboard',
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
    name='TradingDashboard',
)
