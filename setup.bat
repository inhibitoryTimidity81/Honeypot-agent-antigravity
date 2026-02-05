@echo off
echo ========================================
echo Agentic Honeypot - Quick Setup Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/4] Checking environment configuration...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your API keys:
    echo   - GOOGLE_API_KEY: Get from https://ai.google.dev
    echo   - API_KEY: Choose a secure custom key
    echo.
    echo After editing .env, run this script again.
    pause
    exit /b 0
)
echo Environment file found!
echo.

echo [4/4] Starting the application...
echo.
echo The API will be available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo API endpoint: http://localhost:8000/api/honeypot
echo.
echo Press Ctrl+C to stop the server
echo.
python main.py
