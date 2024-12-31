@echo off
setlocal enabledelayedexpansion

REM Function to cleanup on Ctrl+C
:cleanup
echo.
echo 🛑 Interrupted by user
echo 🛑 Stopping containers...
docker compose down
echo ✅ Containers stopped
exit /b 0

REM Handle Ctrl+C
if errorlevel 1 goto cleanup

REM 1. Build Docker containers
echo.
echo Building Docker containers...
docker compose build

REM 2. Start the containers in the background
echo.
echo Starting Docker containers...
docker compose up -d

REM 3. Wait for the application to be ready
echo.
echo Waiting for application to be ready...
timeout /t 5 /nobreak > nul

REM 4. Run tests
echo.
echo Running tests...
pytest

REM Check if tests passed
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
    echo.
    echo You can now access the API at: http://localhost:8000
    echo API documentation available at: http://localhost:8000/docs
    
    REM Show logs and follow them
    echo.
    echo Showing application logs (Ctrl+C to exit):
    docker compose logs -f
) else (
    echo.
    echo Tests failed! Please check the output above.
    exit /b 1
) 