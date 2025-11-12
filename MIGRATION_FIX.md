# Fix: Run Migrations on Render Free Tier

## The Problem
Migrations haven't run, so database tables don't exist.

## Solution: Update Build Command in Render

Since you can't use Shell on free tier, add migrations to the **Build Command**:

### Steps:

1. Go to your Render Web Service → **Settings**
2. Find **Build Command**
3. Update it to:
   ```
   pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
   ```
4. Click **Save Changes**

This will:
- Install dependencies
- Run migrations (creates all tables)
- Collect static files

### Then:

1. Click **Manual Deploy** → **Deploy latest commit**
2. Wait for deployment to complete
3. Your database tables will be created!

## Why This Works

The Build Command runs every time you deploy, so migrations will always run automatically. This is more reliable than relying on the startup script alone.

