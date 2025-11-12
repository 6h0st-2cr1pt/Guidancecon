# Final Build Command for Render

## Copy This Exact Command

Go to Render → Your Web Service → Settings → Build Command

Paste this:

```bash
pip install -r requirements.txt && python manage.py migrate sysadmin 0003_timeslot --fake --noinput && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

## Step by Step

1. Go to https://dashboard.render.com
2. Click on your Web Service
3. Click **Settings** tab
4. Scroll to **Build Command**
5. **Delete** the current command
6. **Paste** the command above
7. Click **Save Changes**
8. Click **Manual Deploy** → **Deploy latest commit**

## What This Does

1. `pip install -r requirements.txt` - Installs packages
2. `python manage.py migrate sysadmin 0003_timeslot --fake --noinput` - **Fakes the problematic migration** (marks it as done without creating table)
3. `python manage.py migrate --noinput` - Runs all other migrations
4. `python manage.py collectstatic --noinput` - Collects static files

This will fix the duplicate table error!

