#!/usr/bin/env bash

# Install Hyperledger Composer and set up the blockchain.

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12
./prereqs-ubuntu.sh

source ~/.nvm/nvm.sh
nvm install 8.9.4

npm install -g grpc --save # avoid g++ errors during the installation
npm install -g composer-cli@0.20
npm install -g composer-rest-server@0.20
npm install -g generator-hyperledger-composer@0.20
npm install -g composer-playground@0.20

./downloadFabric.sh
./createPeerAdminCard.sh

composer card delete --card admin@dwarna-blockchain
./stopFabric.sh
./startFabric.sh
cd dwarna-blockchain/./
