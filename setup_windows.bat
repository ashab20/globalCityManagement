@echo off
echo Setting up Global City Management Application

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

echo Setup complete! 

REM Provide instructions
echo.
echo To run the application:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python main.py

pause
