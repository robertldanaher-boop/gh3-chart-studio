@echo off
rem Double-click to install GH3 Chart Studio for this Windows account:
rem Start menu entry, desktop icon, Settings > Apps entry with Uninstall.
rem No administrator rights needed. Extract the whole ZIP first.
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0installer\install.ps1" %*
exit /b %errorlevel%
