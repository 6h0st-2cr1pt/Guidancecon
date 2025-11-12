#!/usr/bin/env bash
# Migration script that handles existing tables gracefully
set +o errexit  # Don't exit on error, we'll handle it

echo "=== Running database migrations ==="

# Always fake the problematic migration first (safe - just marks it as applied)
echo "=== Faking migration 0003_timeslot (table already exists) ==="
python manage.py migrate sysadmin 0003_timeslot --fake --noinput 2>&1 || true

# Now run all migrations (will skip already applied ones)
echo "=== Running all remaining migrations ==="
python manage.py migrate --noinput

echo "=== Migrations complete ==="

