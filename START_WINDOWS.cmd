@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 goto folder_fail
if not exist tools\startup_windows.py goto missing_files
echo Opening GH3 Chart Studio startup progress...
py -3.11 tools\startup_windows.py 2> startup_bootstrap.log
if errorlevel 1 goto bootstrap_fail
popd
exit /b 0
:missing_files
echo ERROR: Extract the entire ZIP. tools\startup_windows.py is missing.
goto fail
:bootstrap_fail
echo ERROR: Could not run the startup window. Python 3.11 x64 with tkinter is required.
echo Run py -0p to check Python. Re-run the Python installer to add Tcl/Tk if needed.
type startup_bootstrap.log
echo Save startup_bootstrap.log and start_windows.log for troubleshooting.
:fail
pause
popd
exit /b 1
:folder_fail
echo ERROR: Cannot open the application folder.
pause
exit /b 1
