@echo off
cd /d "%~dp0"
set "EXPLORER_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%EXPLORER_PYTHON%" set "EXPLORER_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "%EXPLORER_PYTHON%" (
  echo Please follow README.md to set up the Python environment first.
  pause
  exit /b 1
)
"%EXPLORER_PYTHON%" -m streamlit run "%~dp0streamlit_app.py"
pause
