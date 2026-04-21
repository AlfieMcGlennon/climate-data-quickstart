@echo off
rem One-time setup for the climate-data-quickstart app on Windows.
rem Creates a virtual environment and installs the required packages.
rem Re-run safely: if the venv already exists it is reused.

cd /d "%~dp0"

echo.
echo  Climate data quickstart - setup
echo  ================================
echo.

rem Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found on PATH.
    echo  Install Python 3.10 or later from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\" (
    echo  Creating virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo  Failed to create virtual environment.
        echo  Make sure Python 3.10+ is installed: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo  Activating virtual environment ...
call .venv\Scripts\activate.bat

echo  Upgrading pip ...
python -m pip install --upgrade pip >nul 2>&1

echo  Installing packages (this may take a few minutes) ...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  Package installation failed. Check the error above.
    echo  If cartopy fails, try: conda env create -f environment.yml
    pause
    exit /b 1
)

echo.
echo  ================================
echo  Setup complete.
echo.
echo  To launch the app, double-click run_app.bat
echo  or run: .venv\Scripts\streamlit run app\main.py
echo  ================================
echo.
pause
