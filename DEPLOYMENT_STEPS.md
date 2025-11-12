# Step-by-Step Deployment Checklist

## ✅ Already Done
- [x] requirements.txt created
- [x] settings.py configured for production
- [x] Procfile configured
- [x] Static files configured (WhiteNoise)
- [x] Database URL format supported

## 📋 What You Need to Do Now

### Step 1: Generate Django Secret Key
Run this command in your terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Copy the output** - you'll need it for Step 3.

### Step 2: Push Your Code to Git
Make sure all your changes are committed and pushed:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

### Step 3: Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository (GitHub/GitLab/Bitbucket)
4. Select your repository
5. Configure the service:
   - **Name**: `guidance-connect` (or your preferred name)
   - **Region**: Same region as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `myproject` if needed)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r myproject/requirements.txt`
   - **Start Command**: `cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT`

### Step 4: Set Environment Variables in Render

In your Web Service dashboard, go to **"Environment"** tab and add these:

#### Required Variables:
```
DJANGO_SECRET_KEY=<paste-the-secret-key-from-step-1>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgresql://sysadmin:qQCVuNIBz8NFUenAByqCD2JiXDjtyGvx@dpg-d4a2eb7diees73cr3p8g-a/guidance_8cve
```

**Important**: Replace `your-app-name.onrender.com` with your actual Render app name!

#### Optional Variables (if you need email):
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

### Step 5: Deploy

1. Click **"Create Web Service"** or **"Save Changes"**
2. Render will automatically:
   - Install dependencies
   - Run migrations (from Procfile release command)
   - Collect static files
   - Start your service

### Step 6: Wait and Monitor

1. Watch the build logs in Render dashboard
2. Wait for deployment to complete (5-10 minutes)
3. Check for any errors in the logs

### Step 7: Test Your Deployment

1. Visit your app URL: `https://your-app-name.onrender.com`
2. Test:
   - Public login page loads
   - Admin login works
   - Static files (CSS, images) load correctly
   - Database connection works

### Step 8: Set Up Local Development (Optional)

If you want to develop locally while using Render's database:

1. Get **External Database URL** from Render:
   - Go to your PostgreSQL database in Render
   - Click "Connections" tab
   - Copy "External Connection String"

2. Update your local `.env` file:
```env
DJANGO_SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Use External Database URL (NOT Internal!)
DATABASE_URL=postgresql://sysadmin:password@external-host:port/guidance_8cve

# Optional - email settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

3. Run locally:
```bash
cd myproject
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🎯 Quick Summary

1. ✅ Generate secret key
2. ✅ Push code to Git
3. ✅ Create Web Service on Render
4. ✅ Set environment variables (including DATABASE_URL)
5. ✅ Deploy and test

## ⚠️ Important Notes

- **Internal Database URL** = Use in Render dashboard
- **External Database URL** = Use in local `.env` file
- **Secret Key** = Generate a NEW one for production (don't use dev key)
- **ALLOWED_HOSTS** = Must include your Render app URL

## 🆘 Troubleshooting

If something goes wrong:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Ensure database is running and accessible
4. Check that your app name matches in ALLOWED_HOSTS

