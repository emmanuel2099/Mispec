@echo off
REM Start MISPEC Backend with Local SQLite Database

echo ================================================================================
echo              MISPEC Backend - Local Development Server
echo ================================================================================
echo.
echo [INFO] Using LOCAL SQLite database (no AWS connection needed)
echo.

REM Set Django settings to use local configuration
set DJANGO_SETTINGS_MODULE=mispec.settings_local

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if migrations exist
if not exist "db.sqlite3" (
    echo [INFO] First time setup - Creating local database...
    echo.
    
    echo [STEP 1/3] Running migrations...
    python manage.py migrate --settings=mispec.settings_local
    if errorlevel 1 (
        echo [ERROR] Migration failed
        pause
        exit /b 1
    )
    echo [OK] Database created
    echo.
    
    echo [STEP 2/3] Creating superuser...
    echo.
    echo Please create an admin account:
    python manage.py createsuperuser --settings=mispec.settings_local
    echo.
) else (
    echo [INFO] Database exists, running migrations...
    python manage.py migrate --settings=mispec.settings_local
    echo.
)

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
echo Using LOCAL SQLite database (db.sqlite3)
echo No AWS/Redis connection required!
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

REM Start the server with local settings
python manage.py runserver --settings=mispec.settings_local

pause
