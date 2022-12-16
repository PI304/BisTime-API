echo "Jump to app folder"
cd /home/ubuntu/BisTime-API

echo "Update app from Git - Dev Branch"
git pull origin dev

cd ./infra/scripts
./start.sh