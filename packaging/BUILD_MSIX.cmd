@echo off
setlocal
rem Signed by default. -Unsigned creates a non-installable engineering bundle.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_msix.ps1" %*
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
