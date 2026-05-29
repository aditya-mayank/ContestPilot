@echo off
cd /d "%~dp0..\.."
echo =========================================
echo    ContestPilot - Manual Attendance Review
echo =========================================
echo (Contests are auto-verified, but you can use this to manually review or verify them)
call run.bat --review
pause
