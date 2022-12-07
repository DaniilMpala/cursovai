FROM php:7.4-apache
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
WORKDIR /var/www/html
COPY http-client/build /var/www/html/
RUN mkdir images && chmod 777 -R /var/www

RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN service apache2 restart
