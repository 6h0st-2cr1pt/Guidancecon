# Update Build Command in Render

## The Problem
The table `sysadmin_timeslot` already exists, causing migration to fail.

## Solution: Update Build Command

Go to your Render Web Service → **Settings** → **Build Command**

Replace it with this:

```bash
pip install -r requirements.txt && python manage.py migrate sysadmin 0003_timeslot --fake --noinput && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

## What This Does

1. `pip install -r requirements.txt` - Installs dependencies
2. `python manage.py migrate sysadmin 0003_timeslot --fake --noinput` - **Fakes the problematic migration** (marks it as applied without running it)
3. `python manage.py migrate --noinput` - Runs remaining migrations
4. `python manage.py collectstatic --noinput` - Collects static files

## Steps

1. Copy the command above
2. Go to Render → Your Web Service → Settings
3. Paste into "Build Command" field
4. Click "Save Changes"
5. Click "Manual Deploy" → "Deploy latest commit"

This will fix the duplicate table error!

