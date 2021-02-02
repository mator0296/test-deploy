# solaria

## Celery Local Config

    Open a New Terminal and Start a beat of celery

    celery -A mesada beat -l INFO

    Open a New Terminal and Start a worker

    celery -A mesada worker -B -l INFO

    Run celery flower

    It's important to allow redis to listen all the port in /etc/redis/redis.conf and modify the bind from 127.0.0.1 to 0.0.0.0 to allow redis connect to the docker container

    sudo docker run -it --rm --name flower -p 5555:5555  mher/flower --broker=redis://{local_ip}
