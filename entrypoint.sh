#!/bin/sh

# Wait for the database to be ready
./wait-for-it.sh db 5432

# Run database migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data

# Start the application
gunicorn nokari.wsgi:application --bind 0.0.0.0:8000
