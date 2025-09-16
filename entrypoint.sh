#!/bin/sh

set -e

# Wait for Postgres to be available
until pg_isready -h "db" -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - running migrations"

# Run database migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data

# Start Gunicorn server
exec gunicorn nokari.wsgi:application --bind 0.0.0.0:8000
