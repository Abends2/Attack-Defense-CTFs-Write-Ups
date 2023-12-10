FROM python:3-alpine

RUN apk add --no-cache gcc libc-dev
RUN mkdir /service
WORKDIR /service
ADD util.py util.py
ADD base-requirements.txt base-requirements.txt
RUN pip3 install -r base-requirements.txt
ADD flagbot/* /service/

CMD ["python3", "flagbot.py"]
