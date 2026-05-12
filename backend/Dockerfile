FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias primero (mejor caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000