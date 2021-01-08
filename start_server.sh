#!/bin/bash
set -e

if [ -n "$1" ]; then
    exec "$@"
fi


# Prepare log files and start outputting logs to stdout
touch /var/log/gunicorn.log
touch /var/log/access.log
tail -n 0 -f /var/log/*.log &



echo Starting Gunicorn.
if [ "$ENV" = "development" ] ; then

    (exec gunicorn --reload mesada.wsgi --bind 0.0.0.0:8000)
else
    (exec gunicorn mesada.wsgi \
         --name core \
         --bind 0.0.0.0:8000 \
         --workers 3 \
         --timeout 120 \
         --worker-class gevent \
         --log-level=info \
         --log-file=/var/log/gunicorn.log \
         --access-logfile=/var/log/access.log \
         "$@")
fi
