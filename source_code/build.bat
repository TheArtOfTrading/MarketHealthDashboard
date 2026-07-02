rmdir /s /q build
rmdir /s /q dist
del TradingDashboard.spec

python -m PyInstaller ^
  --onedir ^
  --windowed ^
  --name TradingDashboard ^
  --hidden-import=market_health_dashboard ^
  --hidden-import=us_sector_dashboard ^
  --hidden-import=asx_sector_dashboard ^
  --hidden-import=global_indexes_monthly ^
  --hidden-import=momentum_stocks ^
  --hidden-import=norgatedata ^
  --hidden-import=logbook ^
  --hidden-import=matplotlib.backends.backend_tkagg ^
  trading_dashboard_app.py

pause
