@echo off
cd /d "%~dp0..\.."
echo =========================================
echo    ContestPilot - Clear Google Calendar
echo =========================================
call run.bat --clear-calendar
pause
