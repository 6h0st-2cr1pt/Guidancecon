# Render Setup Configuration

## Current Folder Structure
```
Guidancecon/ (Repository Root)
├── Procfile
├── README.md
└── myproject/ (Django Project Root)
    ├── manage.py
    ├── requirements.txt
    ├── myproject/ (Django Settings)
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── public/ (App)
    └── sysadmin/ (App)
```

## Render Configuration

### Option 1: Root Directory = Empty (Recommended)

**Settings:**
- Root Directory: (leave empty)
- Build Command: `pip install -r myproject/requirements.txt`
- Start Command: `cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT`

**Procfile (current - correct):**
```
web: cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
release: cd myproject && python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

### Option 2: Root Directory = "myproject"

**Settings:**
- Root Directory: `myproject`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn myproject.wsgi --bind 0.0.0.0:$PORT`

**Procfile (needs update):**
```
web: gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

## Recommended: Use Option 1

Keep Root Directory empty and use the current Procfile.

