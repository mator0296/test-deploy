FROM python:3.7

COPY . /app

WORKDIR /app

EXPOSE 8000
ENV TZ America/Caracas
RUN pip uninstall -r requirements.txt -y
RUN pip install -r requirements.txt --upgrade

RUN chmod 0774 /app/start_server.sh

ENTRYPOINT ["/app/start_server.sh"]


