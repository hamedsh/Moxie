FROM python:3.13-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir --upgrade pip && pip install --user -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONPATH=app \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG DB_TYPE=sqlite
ARG DB_PATH=app.db
ARG DB_HOST=
ARG DB_PORT=
ARG DB_USER=
ARG DB_PASSWORD=
ARG DB_DATABASE=

ENV DB_TYPE=${DB_TYPE} \
    DB_PATH=${DB_PATH} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_DATABASE=${DB_DATABASE} \
    PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local

COPY app app
COPY alembic alembic
COPY alembic.ini logging.conf ./

RUN alembic upgrade head

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
