@echo off
REM WildGaurd-Edge Web App Startup Script

echo.
echo ================================================================================
echo                    WildGaurd-Edge: Web Application
echo ================================================================================
echo.
echo Starting Flask web server...
echo.

cd /d "%~dp0"

call .venv\Scripts\activate.bat

python app.py

pause
