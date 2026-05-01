#!/bin/bash

# Start MISPEC Backend with Local SQLite Database

echo "================================================================================"
echo "              MISPEC Backend - Local Development Server"
echo "================================================================================"
echo ""
echo "[INFO] Using LOCAL SQLite database (no AWS connection needed)"
echo ""

# Set Django settings to use local configuration
export DJANGO_SETTINGS_MODULE=mispec.settings_local

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed!"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "[OK] Python is installed"
echo ""

# Check if migrations exist
if [ ! -f "db.sqlite3" ]; then
    echo "[INFO] First time setup - Creating local database..."
    echo ""
    
    echo "[STEP 1/3] Running migrations..."
    $PYTHON_CMD manage.py migrate --settings=mispec.settings_local
    if [ $? -ne 0 ]; then
        echo "[ERROR] Migration failed"
        exit 1
    fi
    echo "[OK] Database created"
    echo ""
    
    echo "[STEP 2/3] Creating superuser..."
    echo ""
    echo "Please create an admin account:"
    $PYTHON_CMD manage.py createsuperuser --settings=mispec.settings_local
    echo ""
else
    echo "[INFO] Database exists, running migrations..."
    $PYTHON_CMD manage.py migrate --settings=mispec.settings_local
    echo ""
fi

echo "================================================================================"
echo "                         Starting Django Server"
echo "================================================================================"
echo ""
echo "Server will start at: http://localhost:8000/"
echo ""
echo "Available URLs:"
echo "  - Swagger UI:  http://localhost:8000/"
echo "  - Admin Panel: http://localhost:8000/admin/"
echo "  - ReDoc:       http://localhost:8000/redoc/"
echo ""
echo "Using LOCAL SQLite database (db.sqlite3)"
echo "No AWS/Redis connection required!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================================================"
echo ""

# Start the server with local settings
$PYTHON_CMD manage.py runserver --settings=mispec.settings_local
