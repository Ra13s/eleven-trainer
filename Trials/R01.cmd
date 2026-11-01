@echo off
cd /d "%~dp0.."
python -m eleven_trainer trial R01 %*
set "trial_exit=%errorlevel%"
pause
exit /b %trial_exit%
