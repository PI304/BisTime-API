docker-compose stop bistime-nginx
sudo certbot renew
cd /home/ubuntu/BisTime-API
. scripts/copy_ssl_files.sh
docker-compose restart bistime-nginx