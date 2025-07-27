@echo off
echo Starting Credit Approval System Manually...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Running database migrations...
python manage.py migrate

echo.
echo Creating superuser (admin/admin123)...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

echo.
echo Ingesting initial data...
python manage.py ingest_data

echo.
echo Starting Django development server...
echo The server will be available at: http://localhost:8000
echo.
python manage.py runserver

pause