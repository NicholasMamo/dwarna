#!/usr/bin/env bash

# Re-install the blockchain from scratch.
# NOTE: The script does not work if there are mounted volumes in `fabric/fabric-scripts/hlfv12/composer/docker-compose.yml`

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source ../variables.sh

echo -e "${HIGHLIGHT}Stopping and removing Hyperledger Fabric${DEFAULT}"
sleep 20s
./stopFabric.sh
./teardownFabric.sh

echo -e "${HIGHLIGHT}Downloading and installing Hyperledger Fabric${DEFAULT}"
./downloadFabric.sh
./startFabric.sh
