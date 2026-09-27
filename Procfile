release: python manage.py migrate --noinput
web: gunicorn --chdir apps/web config.wsgi:application --bind 0.0.0.0:$PORT
