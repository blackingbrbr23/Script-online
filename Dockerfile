# Usa imagem oficial do PHP com Apache
FROM php:8.2-apache

# Copia os arquivos do projeto para dentro do servidor Apache
COPY . /var/www/html/

# Habilita mod_rewrite (opcional, mas bom ter)
RUN a2enmod rewrite

# Expõe a porta 80 (o Render vai mapear automaticamente)
EXPOSE 80

# Inicia o Apache no container
CMD ["apache2-foreground"]
