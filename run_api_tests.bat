@echo off
REM MISPEC API Test Runner Script for Windows
REM This script helps you quickly run API tests

echo ================================================================================
echo                     MISPEC Backend API Test Runner
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install/update dependencies
echo [INFO] Installing test dependencies...
pip install -q -r test_requirements.txt
echo [OK] Dependencies installed
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo [INFO] Creating a template .env file...
    echo BASE_URL=http://localhost:8000 > .env
    echo [OK] Template .env created. Please update it with your settings.
    echo.
)

REM Check if Django server is running
echo [INFO] Checking if Django server is running...
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Cannot connect to http://localhost:8000
    echo [INFO] Make sure your Django server is running:
    echo        python manage.py runserver
    echo.
    set /p continue="Do you want to continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [OK] Server is running
)

echo.
echo ================================================================================
echo                          Running API Tests
echo ================================================================================
echo.

REM Run the tests
python test_all_apis.py

echo.
echo ================================================================================
echo                          Test Run Complete
echo ================================================================================
echo.
echo For more information, see API_TEST_README.md
echo.
pause
