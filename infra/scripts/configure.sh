#!/bin/bash
cd /home/ubuntu/BisTime-API/infra/configs
cp nginx/nginx.conf /etc/nginx
cp -r nginx/conf.d /etc/nginx
cp systemd/gunicorn.socket /etc/systemd/system
cp systemd/gunicorn.service /etc/systemd/system
cd /home/ubuntu/BisTime-API