#!/usr/bin/env bash

source variables.sh

backup=$( date +%Y%m%d )
mkdir -p backup/$backup

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# The Hyperledger Fabric backup copies the admin card and the actual data.
backup_fabric() {
	echo -e "${HIGHLIGHT}Backing up Hyperledger Fabric files${DEFAULT}"
	mkdir -p backup/$1/fabric/dwarna-blockchain
	cp fabric/dwarna-blockchain/admin@dwarna-blockchain.card backup/$1/fabric/dwarna-blockchain

	mkdir -p backup/$1/fabric/fabric-scripts/hlfv12/composer
	cp -r fabric/fabric-scripts/hlfv12/composer/backup_* backup/$1/fabric/fabric-scripts/hlfv12/composer
}

# The REST API backup copies the configuration, including the encryption keys.
backup_rest() {
	echo -e "${HIGHLIGHT}Backing up REST API files${DEFAULT}"
	mkdir -p backup/$1/rest/config
	cp rest/config/*.py backup/$1/rest/config
}

# The WordPress plugin backup copies the configuration, including the encryption key.
backup_plugin() {
	echo -e "${HIGHLIGHT}Backing up WordPress plugin files${DEFAULT}"
	mkdir -p backup/$1/biobank-plugin/includes
	cp biobank-plugin/includes/globals.php backup/$1/biobank-plugin/includes/globals.php
}

# The PostgreSQL backup creates a CSV file of each Dwarna table.
backup_postgresql() {
	echo -e "${HIGHLIGHT}Backing up PostgreSQL database${DEFAULT}"
	mkdir -p backup/$1/postgresql/
	chown postgres backup/$1/postgresql/

	tables=( users researchers participants participant_identities participant_subscriptions biobankers studies studies_researchers emails email_recipients )
	for table in "${tables[@]}"
	do
		su -c "psql -U postgres -d biobank -c \"COPY ${table} TO '${parent_path}/backup/$1/postgresql/${table}.csv' DELIMITER ',' CSV HEADER;\"" postgres
	done
}

# The WordPress backup creates a CSV file of each WordPress table.
backup_wordpress() {
	echo -e "${HIGHLIGHT}Backing up WordPress database${DEFAULT}"
	mkdir -p backup/$1/wordpress/
	mysqldump -u root -p wordpress > backup/$1/wordpress/wordpress.dump
}

backup_fabric $backup
backup_rest $backup
backup_plugin $backup
backup_postgresql $backup
backup_wordpress $backup
