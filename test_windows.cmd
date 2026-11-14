@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Setup is incomplete. Run setup_windows.cmd from this extracted folder first.
  pause
  exit /b 1
)
set QT_QPA_PLATFORM=offscreen
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto fail
echo All automated tests passed. Manual Windows and TheGHOST checks are separate.
pause
exit /b 0
:fail
echo Tests failed. Save the output for diagnostics.
pause
exit /b 1
