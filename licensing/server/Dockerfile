FROM composer:2 AS vendor-dev
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-interaction --prefer-dist --no-scripts

FROM composer:2 AS vendor-prod
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-interaction --prefer-dist --no-scripts --optimize-autoloader

FROM php:8.3-cli-bookworm AS runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libsqlite3-dev \
    && docker-php-ext-install pdo_mysql pdo_sqlite \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/html
COPY . .
COPY docker-entrypoint.sh /usr/local/bin/evepulse-entrypoint
RUN chmod +x /usr/local/bin/evepulse-entrypoint
EXPOSE 8000
ENTRYPOINT ["evepulse-entrypoint"]

FROM runtime AS local
COPY --from=vendor-dev /app/vendor ./vendor
RUN php artisan package:discover --ansi \
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data

FROM runtime AS production
COPY --from=vendor-prod /app/vendor ./vendor
RUN php artisan package:discover --ansi \
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data
