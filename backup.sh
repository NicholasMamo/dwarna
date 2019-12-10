#!/usr/bin/env bash

backup=$( date +%Y%m%d )
mkdir -p backup/$backup

backup_fabric() {
	mkdir -p backup/$1/fabric/dwarna-blockchain
	cp fabric/dwarna-blockchain/admin@dwarna-blockchain.card backup/$1/fabric/dwarna-blockchain

	mkdir -p backup/$1/fabric/fabric-scripts/hlfv12/composer
	cp -r fabric/fabric-scripts/hlfv12/composer/backup_* backup/$1/fabric/fabric-scripts/hlfv12/composer
}

backup_fabric $backup
