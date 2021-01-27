#!/bin/bash
set -e

if [ -n "$1" ]; then
    exec "$@"
fi


# Prepare log files and start outputting logs to stdout
touch /var/log/gunicorn.log
touch /var/log/access.log
tail -n 0 -f /var/log/*.log &

python manage.py migrate &


echo Starting Server.
exec python manage.py runserver
