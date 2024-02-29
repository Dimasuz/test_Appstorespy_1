#!/bin/sh

python3 manage.py collectstatic --noinput --clear

#python3 manage.py makemigrations test_appstorespy_1
python3 manage.py makemigrations

until python3 manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

#gunicorn test_appstorespy_1.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4
python3 manage.py runserver 0.0.0.0:8000
#redis-server

exec "$@"
