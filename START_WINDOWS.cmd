@echo off
setlocal
rem --install (used by the installer and the Repair shortcut): set up and test once, no launch, no pause.
set "GH3_MODE=%~1"
pushd "%~dp0"
if errorlevel 1 goto folder_fail
if not exist tools\startup_windows.py goto missing_files
>startup_bootstrap.log echo GH3 Chart Studio runtime check - %date% %time%
echo Checking Python 3.11 x64 and Tcl/Tk...
set "GH3_PYTHON="
call :probe "%CD%\.venv\Scripts\python.exe"
if defined GH3_PYTHON goto launch
call :probe "%LocalAppData%\Programs\Python\Python311\python.exe"
if defined GH3_PYTHON goto launch
call :probe "%ProgramFiles%\Python311\python.exe"
if defined GH3_PYTHON goto launch
for /f "delims=" %%P in ('py -3.11 -c "import sys;print(sys.executable)" 2^>nul') do call :probe "%%P"
if defined GH3_PYTHON goto launch
echo Python 3.11 with working Tcl/Tk was not found.
echo Downloading and installing the official Python runtime for this user...
call tools\install_python_windows.cmd 2>> startup_bootstrap.log
if errorlevel 1 goto bootstrap_fail
call :probe "%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined GH3_PYTHON goto runtime_fail
:launch
echo Opening GH3 Chart Studio startup progress...
"%GH3_PYTHON%" tools\startup_windows.py %GH3_MODE% 2>> startup_bootstrap.log
if errorlevel 1 goto bootstrap_fail
popd
exit /b 0
:probe
if defined GH3_PYTHON exit /b 0
if not exist "%~1" exit /b 0
"%~1" -c "import sys,struct,tkinter,venv,ensurepip; assert sys.version_info[:2]==(3,11) and struct.calcsize('P')==8; t=tkinter.Tk(); t.withdraw(); t.destroy()" >>startup_bootstrap.log 2>&1
if not errorlevel 1 set "GH3_PYTHON=%~1"
exit /b 0
:runtime_fail
echo ERROR: Python installation finished but the runtime check still failed.
echo If a newer Python 3.11 installation needs repair, use its installer to add Tcl/Tk.
goto bootstrap_fail
:missing_files
echo ERROR: Extract the entire ZIP. tools\startup_windows.py is missing.
goto fail
:bootstrap_fail
echo ERROR: Setup or startup failed. Details follow:
type startup_bootstrap.log
echo Save startup_bootstrap.log, python_install.log if present, and start_windows.log.
:fail
if /i not "%GH3_MODE%"=="--install" pause
popd
exit /b 1
:folder_fail
echo ERROR: Cannot open the application folder.
if /i not "%~1"=="--install" pause
exit /b 1
