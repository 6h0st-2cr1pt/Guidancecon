# How to Run Migrations on Render

## Quick Fix: Use Render Shell

1. Go to your Render Web Service dashboard
2. Click on the **"Shell"** tab (or "Console")
3. Run these commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

This will create all the database tables.

## Alternative: Trigger Manual Deploy

1. Go to your Render Web Service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. This will run the `release` command from Procfile which includes migrations

## Verify Migrations Ran

After running migrations, you can verify in the shell:

```bash
python manage.py showmigrations
```

This will show which migrations have been applied.

