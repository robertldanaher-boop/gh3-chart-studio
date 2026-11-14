@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo First run setup_windows.cmd.
  pause
  exit /b 1
)
.venv\Scripts\python.exe run_app.py
if errorlevel 1 pause
