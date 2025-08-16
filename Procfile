web: python manage.py migrate && python manage.py setup_default_superuser && python manage.py collectstatic --noinput && gunicorn autograde.wsgi:application --bind 0.0.0.0:$PORT
