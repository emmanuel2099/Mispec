@echo off
REM Quick Start Script for MISPEC Backend Server

echo ================================================================================
echo                    MISPEC Backend Server Starter
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Django not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies are installed
)
echo.

REM Run migrations
echo [INFO] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [WARNING] Migration failed, but continuing...
)
echo.

REM Collect static files (optional)
REM echo [INFO] Collecting static files...
REM python manage.py collectstatic --noinput

echo ================================================================================
echo                         Starting Django Server
echo ================================================================================
echo.
echo Server will start at: http://localhost:8000/
echo.
echo Available URLs:
echo   - Swagger UI:  http://localhost:8000/
echo   - Admin Panel: http://localhost:8000/admin/
echo   - ReDoc:       http://localhost:8000/redoc/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

REM Start the server
python manage.py runserver

pause
