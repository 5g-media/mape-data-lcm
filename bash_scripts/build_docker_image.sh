#!/bin/bash

mv mape-data-lcm/ data-lcm/
find ./data-lcm -type d -exec sudo chmod -R 755 {} \;
find ./data-lcm -type f -exec sudo chmod 664 {} \;
chmod a+x ./data-lcm/deployment/run.sh ./data-lcm/deployment/clean.sh
cp ./data-lcm/deployment/Dockerfile .
sudo docker build -t data_lcm .
rm ./Dockerfile
source ./data-lcm/deployment/clean.sh