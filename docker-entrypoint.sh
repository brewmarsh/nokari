#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
./wait-for-it.sh db:5432 --timeout=30

# Run Django migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data

# Start the Gunicorn server
exec gunicorn nokari.wsgi:application --bind 0.0.0.0:8000
