@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please follow README.md to set up the Python environment first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run "%~dp0streamlit_app.py"
pause
