@echo off
echo Starting Credit Approval System...
echo.

echo Checking if Docker is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running. Starting the project...
echo.

echo Building and starting all services...
docker-compose up --build

pause