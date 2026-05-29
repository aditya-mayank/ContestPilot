@echo off
cd /d "%~dp0..\.."
echo =========================================
echo      ContestPilot - Update App
echo =========================================

echo.
echo [1/3] Checking for updates...
call .venv\Scripts\activate.bat 2>nul
python main.py --check-update

echo.
echo [2/3] Pulling latest from GitHub...
git pull

echo.
echo [3/3] Reinstalling dependencies...
pip install -r requirements.txt -q

echo.
echo =========================================
echo  Done! ContestPilot has been updated.
echo =========================================
pause
