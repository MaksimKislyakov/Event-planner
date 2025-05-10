FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /djsite

# Сначала копируем только requirements.txt
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Затем копируем остальные файлы проекта
COPY . .

ENV PYTHONUNBUFFERED=1
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials/client_secret.json

WORKDIR /djsite

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn djsite.wsgi:application --bind 0.0.0.0:8000"]