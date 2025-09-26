# Imagem base Python leve
FROM python:3.11-slim

# Instalar dependências e Firefox
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Instalar Geckodriver fixo (v0.36.0)
RUN GECKO_VERSION=0.36.0 && \
    wget -qO- "https://github.com/mozilla/geckodriver/releases/download/v$GECKO_VERSION/geckodriver-v$GECKO_VERSION-linux64.tar.gz" | tar xz -C /usr/local/bin/

# Criar diretório de trabalho
WORKDIR /app

# Copiar requisitos e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Expor porta padrão do Flask/Render
EXPOSE 5000

# Rodar Xvfb e iniciar Gunicorn
CMD ["xvfb-run", "-a", "gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
