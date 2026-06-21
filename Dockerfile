FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir apache-airflow==2.10.4

COPY . .

ENV PYTHONPATH=/app
