#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting gunicorn..."
exec gunicorn curova_backend.wsgi:application --bind 0.0.0.0:${PORT:-10000}
