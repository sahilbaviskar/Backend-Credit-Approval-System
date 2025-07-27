#!/bin/bash

# Startup script for Credit Approval System

echo "Starting Credit Approval System..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Wait a bit more to ensure database is fully ready
sleep 5

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Ingest initial data from Excel files
echo "Ingesting initial data from Excel files..."
python manage.py ingest_data

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000