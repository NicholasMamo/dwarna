#!/usr/bin/env bash

# Start all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# Start Hyperledger Fabric first
cd fabric
./start_network.sh
cd ..

# Start the REST server
trap ' ' INT # keep the sccript running (do nothing to the script) on keyboard interrupt
python3.7 "rest/main.py"
