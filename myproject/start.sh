#!/usr/bin/env bash
# Startup script that runs migrations before starting the server
set -o errexit

echo "=== Running database migrations ==="
bash run_migrations.sh || {
    echo "Migration had issues, but continuing..."
}

echo "=== Creating admin superuser (if not exists) ==="
python manage.py create_admin || {
    echo "Admin user creation had issues, but continuing..."
}

echo "=== Starting server ==="
exec gunicorn myproject.wsgi --bind 0.0.0.0:$PORT

