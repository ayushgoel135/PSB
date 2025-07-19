#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py populate_sample_data
python manage.py runserver