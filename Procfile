web: bash start.sh
release: cd myproject && bash run_migrations.sh && (python manage.py create_admin || echo "Warning: Admin creation had issues, but continuing deployment...") && python manage.py collectstatic --noinput

