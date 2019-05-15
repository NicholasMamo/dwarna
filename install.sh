#!/usr/bin/env bash

# Install all the components of Dwarna

DEFAULT='\033[0;39m'
HIGHLIGHT='\033[0;36m'

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# Install Hyperledger Fabric first.
echo -e "${HIGHLIGHT}Installing Hyperledger Fabric${DEFAULT}"
cd fabric
./install_network.sh
cd ..
