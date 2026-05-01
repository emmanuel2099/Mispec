@echo off
REM Script to help find your live API URL

echo ================================================================================
echo                    Find Your Live API URL
echo ================================================================================
echo.

echo Checking common deployment platforms...
echo.

REM Check if Heroku CLI is installed
echo [1] Checking Heroku...
heroku --version >nul 2>&1
if errorlevel 1 (
    echo    [X] Heroku CLI not installed
) else (
    echo    [OK] Heroku CLI found
    echo.
    echo    Your Heroku apps:
    heroku apps
    echo.
    echo    To get app URL, run:
    echo    heroku apps:info --app your-app-name
)
echo.

REM Check Procfile for hints
echo [2] Checking Procfile...
if exist "Procfile" (
    echo    [OK] Procfile found - This app is configured for Heroku
    type Procfile
) else (
    echo    [X] No Procfile found
)
echo.

REM Check for deployment configs
echo [3] Checking deployment configs...
if exist "bitbucket-pipelines.yml" (
    echo    [OK] Bitbucket Pipelines found
    echo    Check your Bitbucket pipeline for deployment URL
)
if exist ".github/workflows" (
    echo    [OK] GitHub Actions found
    echo    Check your GitHub Actions for deployment URL
)
echo.

echo ================================================================================
echo                    Common Live API URLs
echo ================================================================================
echo.
echo Based on your project name (MISPEC), your live URL might be:
echo.
echo   Heroku:
echo   - https://mispec-backend.herokuapp.com
echo   - https://mispec-api.herokuapp.com
echo   - https://mispec-dating.herokuapp.com
echo.
echo   Custom Domain:
echo   - https://api.mispec.co.uk
echo   - https://backend.mispec.co.uk
echo   - https://app.mispec.co.uk
echo.
echo   AWS:
echo   - https://mispec-api.us-east-1.elasticbeanstalk.com
echo.
echo ================================================================================
echo                    How to Test Your URL
echo ================================================================================
echo.
echo Once you have your URL, test it:
echo.
echo   curl https://your-url.com/
echo   OR
echo   Open in browser: https://your-url.com/
echo.
echo If it shows Swagger UI, that's your API URL!
echo.
echo ================================================================================
echo                    Update Configuration
echo ================================================================================
echo.
echo After finding your URL:
echo.
echo 1. Update .env file:
echo    BASE_URL = https://your-actual-url.com
echo.
echo 2. Run tests:
echo    python test_all_apis.py
echo.
echo 3. Access Swagger:
echo    https://your-actual-url.com/
echo.
echo ================================================================================
echo.

pause
