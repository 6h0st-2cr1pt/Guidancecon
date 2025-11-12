#!/usr/bin/env bash
# Startup script that runs migrations before starting the server
set -o errexit

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec gunicorn myproject.wsgi --bind 0.0.0.0:$PORT

