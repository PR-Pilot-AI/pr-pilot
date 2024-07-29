#!/bin/bash

python manage.py migrate
uwsgi --ini uwsgi.ini
