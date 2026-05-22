@echo off
cd /d "%~dp0.."
echo =========================================
echo    ContestPilot - Uninstall & Stop
echo =========================================
call run.bat --stop-all
pause
