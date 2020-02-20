#!/usr/bin/env bash

# Install all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

echo -e "${HIGHLIGHT}Installing Schema${DEFAULT}"
cd setup
read -p 'Enter database to install the schema [biobank]: ' database
database=${database:-biobank}
./minimal_schema.py -d $database

echo -e "${HIGHLIGHT}Installing OAuth 2.0 Schema${DEFAULT}"
read -p 'Enter database to install the OAuth schema [biobank_oauth]: ' database
database=${database:-biobank_oauth}
./oauth_schema.py -d $database
cd ..

# Install Hyperledger Fabric first.
echo -e "${HIGHLIGHT}Installing Hyperledger Fabric${DEFAULT}"
cd fabric
./install_network.sh
cd ..
