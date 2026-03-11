FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt
COPY app app
COPY logging.conf .

ENV PYTHONPATH=app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
