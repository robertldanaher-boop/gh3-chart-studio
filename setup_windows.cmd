@echo off
setlocal
cd /d "%~dp0"
py -3.11 -c "import struct; assert struct.calcsize('P') == 8, 'Install 64-bit Python'"
if errorlevel 1 goto fail
if not exist .venv\Scripts\python.exe py -3.11 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock
if errorlevel 1 goto fail
echo Setup complete. Double-click launch_windows.cmd.
pause
exit /b 0
:fail
echo Setup failed. Install Python 3.11 x64 with the Python launcher, then try again.
pause
exit /b 1
