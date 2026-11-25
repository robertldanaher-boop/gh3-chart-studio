@echo off
setlocal
rem Signed by default. Use -Unsigned only for a labelled development build.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_installer.ps1" %*
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo Installer build or signing failed. See the error above.
pause
exit /b %RESULT%
