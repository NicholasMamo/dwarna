#!/usr/bin/env bash

# Re-install the blockchain from scratch.
# NOTE: The script does not work if there are mounted volumes in `fabric/fabric-scripts/hlfv12/composer/docker-compose.yml`

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12

./stopFabric.sh
./teardownFabric.sh
./downloadFabric.sh
./startFabric.sh
