# Render Configuration Guide

## Your Current Structure
```
Guidancecon/ (Git Repository Root)
├── Procfile
├── README.md
└── myproject/ (Django Project - This is where manage.py and requirements.txt are)
    ├── manage.py
    ├── requirements.txt
    ├── myproject/ (Django settings folder)
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── public/ (App)
    └── sysadmin/ (App)
```

## ✅ RECOMMENDED: Set Root Directory to "myproject"

### In Render Dashboard:

1. Go to your Web Service → **Settings**
2. Set **Root Directory** to: `myproject`
3. Set **Build Command** to:
   ```
   pip install -r requirements.txt
   ```
4. Set **Start Command** to:
   ```
   gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
   ```

### Update Procfile for this setup:
The Procfile should be updated to work from the myproject directory.

