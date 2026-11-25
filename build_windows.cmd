@echo off
setlocal
cd /d "%~dp0"
.venv\Scripts\python.exe -c "import sys,struct; assert sys.platform=='win32' and sys.version_info[:2]==(3,11) and struct.calcsize('P')==8"
if errorlevel 1 goto fail
set QT_QPA_PLATFORM=offscreen
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto fail
set QT_QPA_PLATFORM=
.venv\Scripts\python.exe tools\freeze_app.py
if errorlevel 1 goto fail
if /I "%~1"=="-Unsigned" (
  echo UNSIGNED DEVELOPMENT BUILD: dist\GH3ChartStudio\GH3ChartStudio.exe
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File installer\sign.ps1 -Path dist\GH3ChartStudio\GH3ChartStudio.exe -ReportPath dist\GH3ChartStudio-signature.json
  if errorlevel 1 goto fail
  echo Signed and verified dist\GH3ChartStudio\GH3ChartStudio.exe.
)
echo Keep the entire folder together. MSIX is the primary package: packaging\BUILD_MSIX.cmd.
echo Manual Windows and dependency redistribution acceptance remain required.
pause
exit /b 0
:fail
echo Build stopped because a prerequisite, test, or packaging step failed.
pause
exit /b 1
