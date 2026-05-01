#!/bin/bash

# MISPEC API Test Runner Script
# This script helps you quickly run API tests

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    MISPEC Backend API Test Runner                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✓ Using Python: $($PYTHON_CMD --version)"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    $PYTHON_CMD -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
echo "✓ Virtual environment activated"
echo ""

# Install/update dependencies
echo "📥 Installing test dependencies..."
pip install -q -r test_requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating a template .env file..."
    echo "BASE_URL=http://localhost:8000" > .env
    echo "✓ Template .env created. Please update it with your settings."
    echo ""
fi

# Check if Django server is running
echo "🔍 Checking if Django server is running..."
BASE_URL=$(grep BASE_URL .env | cut -d '=' -f2 | tr -d ' ')
if [ -z "$BASE_URL" ]; then
    BASE_URL="http://localhost:8000"
fi

if curl -s "$BASE_URL" > /dev/null 2>&1; then
    echo "✓ Server is running at $BASE_URL"
else
    echo "⚠️  Warning: Cannot connect to $BASE_URL"
    echo "   Make sure your Django server is running:"
    echo "   $ python manage.py runserver"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                         Running API Tests                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Run the tests
$PYTHON_CMD test_all_apis.py

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                         Test Run Complete                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 For more information, see API_TEST_README.md"
echo ""
