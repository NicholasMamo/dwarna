#!/usr/bin/env bash

# Install all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source ../variables.sh

# Install Hyperledger Fabric first.
echo -e "${HIGHLIGHT}Installing Hyperledger Fabric${DEFAULT}"
cd fabric
./install_network.sh
cd ..
