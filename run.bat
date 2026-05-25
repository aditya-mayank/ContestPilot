@echo off
setlocal
cd /d "%~dp0"

echo [ContestPilot] Starting up...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [ContestPilot] Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies
echo [ContestPilot] Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

:: Run the main program
echo [ContestPilot] Running application...
.\.venv\Scripts\python main.py %*

if "%1"=="" (
    echo [ContestPilot] Done.
    pause
)
