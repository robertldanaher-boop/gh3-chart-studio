@echo off
setlocal
cd /d "%~dp0"
.venv\Scripts\python.exe -c "import sys,struct; assert sys.platform=='win32' and sys.version_info[:2]==(3,11) and struct.calcsize('P')==8"
if errorlevel 1 goto fail
set QT_QPA_PLATFORM=offscreen
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto fail
set QT_QPA_PLATFORM=
.venv\Scripts\python.exe tools\collect_licenses.py
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name GH3ChartStudio --collect-all imageio_ffmpeg --add-data "LICENSE;." --add-data "docs;docs" --add-data "licenses;licenses" --add-data "examples;examples" run_app.py
if errorlevel 1 goto fail
echo Built dist\GH3ChartStudio\GH3ChartStudio.exe. Keep the entire folder together.
echo This build still needs the manual acceptance test in docs\WINDOWS_TEST.md.
pause
exit /b 0
:fail
echo Build stopped because a prerequisite, test, or packaging step failed.
pause
exit /b 1
