#!/bin/sh

set -e

./manage.py migrate
./manage.py create_admin

case "$LAYER" in
  dev )
    echo "run by hand:"
    echo "docker-compose exec backend python manage.py runserver 0.0.0.0:8000"
    tail -f /dev/null  # do nothing, forever
    ;;
  * )
    exec gunicorn --bind=0.0.0.0:8000 mysite.wsgi:application
    ;;
esac
