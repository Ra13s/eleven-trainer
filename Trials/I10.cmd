@echo off
cd /d "%~dp0.."
python -m eleven_trainer trial I10 %*
set "trial_exit=%errorlevel%"
pause
exit /b %trial_exit%
