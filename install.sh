#!/usr/bin/env bash

# Install all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

echo -e "${HIGHLIGHT}Installing Schema${DEFAULT}"
cd setup
./minimal_schema.py
echo -e "${HIGHLIGHT}Installing OAuth 2.0 Schema${DEFAULT}"
./oauth_schema.py
cd ..

# Install Hyperledger Fabric first.
echo -e "${HIGHLIGHT}Installing Hyperledger Fabric${DEFAULT}"
cd fabric
./install_network.sh
cd ..
