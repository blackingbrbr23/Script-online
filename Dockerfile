FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Rodar Xvfb automaticamente ao iniciar
CMD ["xvfb-run", "-a", "gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
