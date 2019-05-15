#!/usr/bin/env bash

# Start all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

# Start Hyperledger Fabric first.
echo -e "${HIGHLIGHT}Starting Hyperledger Fabric${DEFAULT}"
cd fabric
./start_network.sh
cd ..

# Start the REST server.
echo -e "${HIGHLIGHT}Starting REST API${DEFAULT}"
trap ' ' INT # keep the sccript running (do nothing to the script) on keyboard interrupt
python3.7 "rest/main.py"
