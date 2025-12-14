#!/usr/bin/env bash
# Startup script that runs migrations before starting the server
set -e  # Exit on error

# Change to the project directory
cd /opt/render/project/src/myproject || cd "$(dirname "$0")"

echo "=== Running database migrations ==="
bash run_migrations.sh || {
    echo "Migration had issues, but continuing..."
}

echo "=== Creating admin superuser (if not exists) ==="
echo "Current directory: $(pwd)"
echo "Running: python manage.py create_admin"
python manage.py create_admin 2>&1 || {
    echo "ERROR: Admin user creation had issues, but continuing..."
    echo "This might prevent admin login. Check logs above for details."
}

echo "=== Starting server ==="
exec gunicorn myproject.wsgi --bind 0.0.0.0:$PORT

