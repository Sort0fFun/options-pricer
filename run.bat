@echo off
REM Batch startup script for NSE Options Pricer Flask app

echo ========================================
echo NSE Options Pricer - Flask Edition
echo ========================================

REM Check if venv exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please create one with: python -m venv venv
    exit /b 1
)

REM Load environment variables from .env file
if exist ".env" (
    for /f "usebackq tokens=*" %%a in (".env") do (
        set "line=%%a"
        REM Skip empty lines and comments
        if not "!line!"=="" if not "!line:~0,1!"=="#" (
            set "%%a"
        )
    )
    echo Loaded environment variables from .env
)

REM Set Flask environment variables
set FLASK_ENV=development
set FLASK_PORT=5001

echo.
echo Starting Flask app on port 5001...
echo Once started, visit: http://localhost:5001
echo.
echo Press CTRL+C to stop the server
echo ----------------------------------------
echo.

REM Use venv Python
venv\Scripts\python.exe flask_app.py
