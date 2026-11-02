FROM php:8.2-apache

COPY index.php /var/www/html/index.php
COPY uploads.conf /etc/apache2/conf-available/uploads.conf

RUN a2enconf uploads \
    && mkdir -p /var/www/html/uploads \
    && chown -R www-data:www-data /var/www/html/uploads

# La flag vive en el sistema de ficheros del contenedor.
RUN printf 'RUBIK{file_upload_doble_extension}\n' > /flag.txt

EXPOSE 80
