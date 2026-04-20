@echo off
rem Launches the climate-data-quickstart Streamlit app on Windows.
rem Expects setup.bat to have been run first.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo .venv not found. Run setup.bat first to install dependencies.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
streamlit run app\main.py
