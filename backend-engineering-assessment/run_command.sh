#!/usr/bin/env bash

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput
python manage.py init_db
python manage.py runserver 0.0.0.0:8000
