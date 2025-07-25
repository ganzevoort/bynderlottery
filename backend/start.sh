#!/bin/sh

set -e

mkdir -p logs

python checkdb.py
./manage.py migrate
./manage.py create_admin

case "$LAYER" in
  debug )
    echo "run by hand:"
    echo "docker-compose exec backend python manage.py runserver 0.0.0.0:8000"
    tail -f /dev/null  # do nothing, forever
    ;;
  dev )
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  * )
    exec gunicorn --bind=0.0.0.0:8000 mysite.wsgi:application
    ;;
esac
