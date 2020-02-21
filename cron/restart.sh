#!/usr/bin/env bash

kill $(lsof -t -i:3000);
kill $(lsof -t -i:3001);
export PATH=$PATH:/usr/local/bin/
cd /mnt/DATA/dwarna/
./fabric/start_network.sh > /var/log/fabric/$( date +%Y%m%d ).log
