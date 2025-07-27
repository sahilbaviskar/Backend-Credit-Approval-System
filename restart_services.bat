@echo off
echo Stopping existing containers...
docker-compose down

echo Removing old images to force rebuild...
docker-compose build --no-cache

echo Starting services with health checks...
docker-compose up -d

echo Waiting for services to be healthy...
timeout /t 30

echo Checking service status...
docker-compose ps

echo.
echo Services should now be running with fixes applied:
echo - Celery broker connection retry warning fixed
echo - Database migrations will run automatically
echo - Health check endpoint improved with service status
echo - Better service dependency management
echo.
echo You can check the health status at: http://localhost:8000/health/
echo.
pause