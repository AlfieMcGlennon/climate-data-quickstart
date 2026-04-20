@echo off
rem One-time setup for the climate-data-quickstart app on Windows.
rem Creates a virtual environment and installs the required packages.
rem Re-run safely: if the venv already exists it is reused.

cd /d "%~dp0"

if not exist ".venv\" (
    echo Creating virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo Failed to create a virtual environment. Make sure Python 3.10 or
        echo later is installed and on PATH: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo Activating virtual environment ...
call .venv\Scripts\activate.bat

echo Upgrading pip ...
python -m pip install --upgrade pip >nul

echo Installing requirements (this may take a few minutes) ...
python -m pip install -r requirements.txt

echo.
echo Setup complete. Double-click run_app.bat to launch the app.
pause
