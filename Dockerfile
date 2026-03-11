FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

COPY app/api app/api
COPY app/core app/core
COPY app/__init__.py app
COPY app/main.py app

COPY alembic alembic
COPY alembic.ini .
COPY logging.conf .

ENV PYTHONPATH=app

# Build-time arguments
ARG DB_TYPE=sqlite
ARG DB_PATH=app.db
ARG DB_HOST=
ARG DB_PORT=
ARG DB_USER=
ARG DB_PASSWORD=
ARG DB_DATABASE=

# Set environment variables
ENV DB_TYPE=${DB_TYPE}
ENV DB_PATH=${DB_PATH}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_DATABASE=${DB_DATABASE}


RUN alembic upgrade head;

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
