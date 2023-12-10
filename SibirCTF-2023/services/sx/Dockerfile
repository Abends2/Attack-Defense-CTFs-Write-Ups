FROM python:3.10

WORKDIR /service

COPY ./requirements.txt /service/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /service/requirements.txt

COPY ./app /service/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3080"]
