# Imagem oficial PHP com Apache
FROM php:8.2-apache

# Copia arquivos do projeto para dentro do servidor Apache
COPY . /var/www/html/

# Expõe a porta
EXPOSE 80
