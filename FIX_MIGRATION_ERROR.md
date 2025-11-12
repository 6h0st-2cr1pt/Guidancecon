# Fix: Duplicate Table Error

## Problem
The table `sysadmin_timeslot` already exists, but Django is trying to create it again.

## Solution: Use --fake-initial flag

Update your Build Command in Render to:

```
pip install -r requirements.txt && python manage.py migrate --fake-initial --noinput && python manage.py collectstatic --noinput
```

The `--fake-initial` flag will:
- Skip creating tables that already exist
- Mark migrations as applied if their tables are already in the database
- Continue with remaining migrations

This is safe and won't cause data loss.

