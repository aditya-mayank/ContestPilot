@echo off
echo =========================================
echo   ContestPilot Background Automation
echo =========================================
echo.
set "TASK_NAME=ContestPilotDaily"
set "VBS_PATH=%~dp0run_invisible.vbs"
set "BAT_PATH=%~dp0run.bat"

echo Installing Windows Scheduled Task...
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%VBS_PATH%\" \"%BAT_PATH%\"" /sc daily /st 08:00 /f

echo.
echo [Success] ContestPilot will now run silently every morning at 8:00 AM!
echo To completely uninstall and stop this, run: .\run.bat --stop-all
echo.
pause
