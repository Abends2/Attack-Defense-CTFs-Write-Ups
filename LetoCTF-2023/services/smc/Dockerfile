FROM python:3.9-alpine

RUN apk add --update build-base gcc postgresql-dev

WORKDIR /task

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY config.py .
COPY entrypoint.sh .
COPY run.py .
COPY src src

#CMD gunicorn --bind 0.0.0.0:1337 --log-level debug run:app
ENTRYPOINT  [ "/task/entrypoint.sh" ]
