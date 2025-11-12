# Final Build Command - Fix All Migration Issues

## Update Build Command in Render

Go to Render → Your Web Service → Settings → Build Command

**Replace with this exact command:**

```bash
pip install -r requirements.txt && python manage.py migrate sysadmin 0003_timeslot --fake --noinput && python manage.py migrate sysadmin 0004_delete_counselor --fake --noinput && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

## What This Does

1. Installs dependencies
2. Fakes migration 0003 (timeslot table already exists)
3. Fakes migration 0004 (counselor table doesn't exist, so deletion is already done)
4. Runs all remaining migrations (including the new 0005 that adds custom fields)
5. Collects static files

## Steps

1. Copy the command above
2. Go to Render → Your Web Service → Settings
3. Paste into "Build Command"
4. Save Changes
5. Manual Deploy → Deploy latest commit

This will fix all migration issues!

