#!/usr/bin/env bash

# Install Hyperledger Composer and set up the blockchain.

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source ../variables.sh

echo -e "${HIGHLIGHT}Installing NPM${DEFAULT}"
source ~/.nvm/nvm.sh
nvm install 8.9.4

echo -e "${HIGHLIGHT}Installing NPM dependencies${DEFAULT}"
npm install -g grpc --save # avoid g++ errors during the installation
npm install -g composer-cli@0.20
npm install -g composer-rest-server@0.20
npm install -g generator-hyperledger-composer@0.20
npm install -g composer-playground@0.20

echo -e "${HIGHLIGHT}Installing Hyperledger Fabric prerequisites${DEFAULT}"
./prereqs-ubuntu.sh

echo -e "${HIGHLIGHT}Downloading Hyperledger Fabric${DEFAULT}"
./downloadFabric.sh

echo -e "${HIGHLIGHT}Installing Hyperledger Fabric${DEFAULT}"
./createPeerAdminCard.sh
composer card delete --card admin@dwarna-blockchain
./stopFabric.sh
./startFabric.sh
