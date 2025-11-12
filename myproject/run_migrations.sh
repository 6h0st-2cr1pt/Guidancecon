#!/usr/bin/env bash
# Migration script that handles existing tables gracefully
set +o errexit  # Don't exit on error, we'll handle it

echo "=== Running database migrations ==="

# Fake problematic migrations that have inconsistent state
echo "=== Faking migration 0003_timeslot (table already exists) ==="
python manage.py migrate sysadmin 0003_timeslot --fake --noinput 2>&1 || true

echo "=== Faking migration 0004_delete_counselor (table doesn't exist) ==="
python manage.py migrate sysadmin 0004_delete_counselor --fake --noinput 2>&1 || true

# Now run all migrations (will skip already applied ones)
echo "=== Running all remaining migrations ==="
python manage.py migrate --noinput

echo "=== Migrations complete ==="

