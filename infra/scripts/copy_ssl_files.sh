cd /home/ubuntu/BisTime-API
sudo rm -r /certs
mkdir certs
cd certs
sudo cp /etc/letsencrypt/live/bistime.app/fullchain.pem /home/ubuntu/BisTime-API/certs/
sudo cp /etc/letsencrypt/live/bistime.app/privkey.pem /home/ubuntu/BisTime-API/certs/
sudo cp /etc/letsencrypt/options-ssl-nginx.conf /home/ubuntu/BisTime-API/certs/
sudo cp /etc/letsencrypt/ssl-dhparams.pem /home/ubuntu/BisTime-API/certs/