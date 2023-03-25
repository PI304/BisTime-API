#!/bin/bash

docker run --rm --name certbot \
-v '/home/ubuntu/BisTime-API/certbot/conf:/etc/letsencrypt' \
-v '/home/ubuntu/BisTime-API/certbot/logs:/var/log/letsencrypt' \
-v '/home/ubuntu/BisTime-API/certbot/data:/var/www/letsencrypt' \
certbot/certbot certonly --webroot -w /var/www/letsencrypt --force-renewal --server https://acme-v02.api.letsencrypt.org/directory \
--cert-name api.bistime.app

docker exec bistime-nginx nginx -s reload