# Imagem base Python leve
FROM python:3.11-slim

# Instalar Firefox, Geckodriver e dependências
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requisitos e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor a porta que o Render usa
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
