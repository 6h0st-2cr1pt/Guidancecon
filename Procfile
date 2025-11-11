web: cd myproject && gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
release: cd myproject && python manage.py migrate --noinput && python manage.py collectstatic --noinput

