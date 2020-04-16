#!/bin/bash

if sudo docker ps | grep -q 'data_lcm'; then
    sudo docker exec -i data_lcm service supervisor stop && \
    sudo docker stop data_lcm && \
    sudo docker rm -f data_lcm
fi
