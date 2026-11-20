@echo off
rem Build the Windows installer locally. Requires Inno Setup 6.3+ (free):
rem   https://jrsoftware.org/isdl.php
rem The GitHub Actions workflow does the same thing automatically.
setlocal
cd /d "%~dp0"
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 was not found. Install it from https://jrsoftware.org/isdl.php and run this again.
  pause
  exit /b 1
)
set "VERSION="
for /f "tokens=2 delims='" %%V in ('findstr /b "__version__" ..\gh3studio\__init__.py') do set "VERSION=%%V"
if not defined VERSION (
  echo Could not read the version from gh3studio\__init__.py
  pause
  exit /b 1
)
echo Building GH3 Chart Studio %VERSION% installer...
"%ISCC%" /DAppVersion=%VERSION% GH3ChartStudio.iss
if errorlevel 1 (
  echo Installer build failed.
  pause
  exit /b 1
)
echo Done: installer\output\GH3ChartStudio-Setup-%VERSION%.exe
pause
