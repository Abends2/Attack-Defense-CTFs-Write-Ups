FROM python:3-alpine

RUN apk add --no-cache gcc libc-dev
RUN mkdir /service
WORKDIR /service
ADD util.py util.py
ADD base-requirements.txt base-requirements.txt
RUN pip3 install -r base-requirements.txt
ADD service02 /service/
RUN pip3 install -r requirements.txt

CMD ["gunicorn", "-c", "gunicorn.conf.py", "service:app"]
