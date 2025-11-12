# Render Deployment Guide

This guide will help you deploy the Guidance Connect application to Render's free tier.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Render account (sign up at https://render.com)
3. Your code pushed to a Git repository

## Step 1: Prepare Your Repository

1. Make sure all your changes are committed and pushed to your Git repository
2. Ensure `.env` file is in `.gitignore` (never commit secrets!)

## Step 2: Create PostgreSQL Database on Render

1. Go to Render Dashboard → New → PostgreSQL
2. Choose the **Free** plan
3. Name your database (e.g., `guidance-connect-db`)
4. Select a region closest to you
5. Click "Create Database"
6. Wait for the database to be created
7. **Copy the Internal Database URL** - you'll need this later

## Step 3: Create Web Service on Render

1. Go to Render Dashboard → New → Web Service
2. Connect your Git repository
3. Configure the service:
   - **Name**: `guidance-connect` (or your preferred name)
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `myproject` if your structure is different)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r myproject/requirements.txt`
   - **Start Command**: `cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT`

## Step 4: Configure Environment Variables

In your Render Web Service dashboard, go to **Environment** tab and add:

### Required Variables:

```
DJANGO_SECRET_KEY=your-secret-key-here-generate-a-random-one
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1
DATABASE_URL=<paste-the-internal-database-url-from-step-2>
```

### Optional Variables (for email functionality):

```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

### Generate Django Secret Key:

Run this in your terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations (from the `release` command in Procfile)
   - Collect static files
   - Start the web service

## Step 6: Verify Deployment

1. Wait for the deployment to complete (usually 5-10 minutes)
2. Visit your app URL: `https://your-app-name.onrender.com`
3. Test the application:
   - Public login page should load
   - Admin login should work
   - Static files (CSS, images) should load correctly

## Local Development Setup

To continue developing locally while using Render's database:

1. Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Use Render's External Database URL (not Internal!)
# Get this from Render Database dashboard → Connections → External Connection String
DATABASE_URL=postgresql://user:password@host:port/database

# Or use individual variables:
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=your_db_host
# DB_PORT=5432

# Optional - for email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

2. Install dependencies:
```bash
cd myproject
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (if needed):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Important Notes

### Media Files Warning
⚠️ **On Render's free tier, uploaded media files (profile pictures, etc.) are ephemeral and will be lost on redeploy.**

Solutions:
- Use cloud storage (AWS S3, Cloudinary, etc.) for production
- For now, media files will work but won't persist across redeployments

### Database Connection
- **Internal Database URL**: Use this in Render Web Service (faster, free)
- **External Database URL**: Use this for local development

### Static Files
- Static files are automatically collected and served via WhiteNoise
- No additional configuration needed

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- 750 hours/month free (enough for 24/7 operation)
- Database has 90-day data retention on free tier

## Troubleshooting

### Static files not loading
- Check that `collectstatic` ran successfully in build logs
- Verify `STATIC_ROOT` is set correctly
- Ensure WhiteNoise middleware is in `MIDDLEWARE` list

### Database connection errors
- Verify `DATABASE_URL` is set correctly
- Check database is running in Render dashboard
- Ensure you're using Internal URL for Render service, External for local

### Email not working
- Verify email credentials are set correctly
- Check Gmail App Password is used (not regular password)
- Email will use console backend if credentials not provided

### 500 errors
- Check Render logs for detailed error messages
- Ensure `DEBUG=False` in production
- Verify all environment variables are set

## Updating Your Application

1. Make changes locally
2. Test thoroughly
3. Commit and push to Git
4. Render will automatically detect changes and redeploy
5. Monitor the deployment logs

## Support

For issues:
- Check Render logs in the dashboard
- Review Django logs
- Ensure all environment variables are correct
- Verify database is accessible

