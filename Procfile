release: python manage.py makemigrations users && python manage.py makemigrations core && python manage.py migrate
web: gunicorn wway.wsgi