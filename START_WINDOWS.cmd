@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 goto folder_fail
set "studio_log=%CD%\start_windows.log"
> "%studio_log%" echo GH3 Chart Studio startup - %date% %time%
if not exist requirements-windows.lock goto missing_files
if not exist run_app.py goto missing_files

echo [1/3] Setting up GH3 Chart Studio...
echo Details are being saved to start_windows.log.
py -3.11 -c "import struct; assert struct.calcsize('P') == 8, 'Python 3.11 must be 64-bit'" >> "%studio_log%" 2>&1
if errorlevel 1 goto python_fail
if not exist ".venv\Scripts\python.exe" (
    py -3.11 -m venv .venv >> "%studio_log%" 2>&1
    if errorlevel 1 goto setup_fail
)
".venv\Scripts\python.exe" -c "import sys,struct; assert sys.version_info[:2] == (3,11) and struct.calcsize('P') == 8, 'Existing .venv must use Python 3.11 x64'" >> "%studio_log%" 2>&1
if errorlevel 1 goto setup_fail
".venv\Scripts\python.exe" -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock >> "%studio_log%" 2>&1
if errorlevel 1 goto setup_fail

echo [2/3] Running automated tests. Please wait...
set "QT_QPA_PLATFORM=offscreen"
".venv\Scripts\python.exe" -m pytest -q >> "%studio_log%" 2>&1
if errorlevel 1 goto test_fail
set "QT_QPA_PLATFORM="

echo [3/3] Tests passed. Opening GH3 Chart Studio...
".venv\Scripts\python.exe" run_app.py >> "%studio_log%" 2>&1
if errorlevel 1 goto launch_fail
popd
exit /b 0

:missing_files
echo ERROR: Place START_WINDOWS.cmd beside run_app.py and requirements-windows.lock.
echo Extract the entire application ZIP first.
goto fail
:python_fail
echo ERROR: Python 3.11 x64 or the Python launcher could not be started.
echo Run py -0p to check installed versions. Python 3.11.0 specifically is not required.
goto fail
:setup_fail
echo ERROR: Setup failed. The application was not launched.
echo Check the log for an installation, network, or existing virtual-environment error.
goto fail
:test_fail
echo ERROR: Automated tests failed. The application was not launched.
goto fail
:launch_fail
echo ERROR: The application exited with an error.
goto fail
:fail
echo.
echo Diagnostic log: "%studio_log%"
echo.
type "%studio_log%"
echo.
pause
popd
exit /b 1
:folder_fail
echo ERROR: Cannot open the folder containing START_WINDOWS.cmd.
pause
exit /b 1
