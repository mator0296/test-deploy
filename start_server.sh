#!/bin/bash
set -e

if [ -n "$1" ]; then
    exec "$@"
fi

echo starting logs

# Prepare log files and start outputting logs to stdout
touch /var/log/gunicorn.log
touch /var/log/access.log
tail -n 0 -f /var/log/*.log &


echo Starting Server.
exec gunicorn mesada.wsgi \
        --bind 0.0.0.0:8000 \
        --log-level=info \
        --log-file=/var/log/gunicorn.log \
        --access-logfile=/var/log/access.log \
        "$@"
