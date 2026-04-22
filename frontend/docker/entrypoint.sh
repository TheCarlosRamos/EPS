#!/bin/sh
set -eu

: "${NGINX_BACKEND_UPSTREAM:=host.docker.internal:8000}"

mkdir -p /etc/nginx/certs

if [ ! -f /etc/nginx/certs/fullchain.pem ] || [ ! -f /etc/nginx/certs/privkey.pem ]; then
  openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
    -keyout /etc/nginx/certs/privkey.pem \
    -out /etc/nginx/certs/fullchain.pem \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
fi

envsubst '$NGINX_BACKEND_UPSTREAM' \
  < /etc/nginx/templates/nginx.conf.template \
  > /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'