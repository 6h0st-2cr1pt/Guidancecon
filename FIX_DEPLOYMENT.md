# Fix Render Deployment - Step by Step

## Problem
Render can't find `myproject/requirements.txt` because the Root Directory setting doesn't match the folder structure.

## Solution: Set Root Directory to "myproject"

### Step 1: Update Render Dashboard Settings

1. Go to your Render Web Service
2. Click **Settings** tab
3. Find **Root Directory** field
4. Set it to: `myproject`
5. Click **Save Changes**

### Step 2: Update Build & Start Commands

In the same Settings page:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
```

### Step 3: Commit Updated Procfile

The Procfile has been updated. Commit it:

```bash
git add Procfile
git commit -m "Update Procfile for Render deployment"
git push
```

### Step 4: Redeploy

Render will automatically redeploy when you push, or you can manually trigger a deploy.

## Why This Works

- **Root Directory = "myproject"** means Render starts in the `myproject/` folder
- From there, `requirements.txt` is directly accessible (no `myproject/` prefix needed)
- `manage.py` is also directly accessible
- The `myproject.wsgi` path is correct because we're already in the `myproject/` folder

## Alternative: Keep Root Directory Empty

If you prefer to keep Root Directory empty, use these commands:

**Build Command:**
```
pip install -r myproject/requirements.txt
```

**Start Command:**
```
cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
```

But the first solution (Root Directory = "myproject") is cleaner and recommended.

