#!/usr/bin/env bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

source variables.sh

# Create the backup's output directory.
create_dir() {
	output='backup'
	for ((i=0; i<$#; i++)); do
		if [ "${!i}" = '-o' ]; then
			let "value=$i+1"
			output=${!value}
			break
		fi
	done

	backup=$( date +%Y%m%d )
	mkdir -p $output/$backup
	echo "$output/$backup"
}

usage() {
	echo -e "${HIGHLIGHT}Usage: $0 [-o backup/] [-h] [--blockchain] [--rest] [--plugin] [--postgresql] [--wordpress]${DEFAULT}";
}

# The Hyperledger Fabric backup copies the admin card and the actual data.
backup_fabric() {
	echo -e "${HIGHLIGHT}Backing up Hyperledger Fabric files${DEFAULT}"
	mkdir -p $1/fabric/dwarna-blockchain
	cp fabric/dwarna-blockchain/admin@dwarna-blockchain.card $1/fabric/dwarna-blockchain

	mkdir -p $1/fabric/fabric-scripts/hlfv12/composer
	cp -r fabric/fabric-scripts/hlfv12/composer/backup_* $1/fabric/fabric-scripts/hlfv12/composer
}

# The REST API backup copies the configuration, including the encryption keys.
backup_rest() {
	echo -e "${HIGHLIGHT}Backing up REST API files${DEFAULT}"
	mkdir -p $1/rest/config
	cp rest/config/*.py $1/rest/config
}

# The WordPress plugin backup copies the configuration, including the encryption key.
backup_plugin() {
	echo -e "${HIGHLIGHT}Backing up WordPress plugin files${DEFAULT}"
	mkdir -p $1/biobank-plugin/includes
	cp biobank-plugin/includes/globals.php $1/biobank-plugin/includes/globals.php
}

# The PostgreSQL backup creates a CSV file of each Dwarna table.
backup_postgresql() {
	echo -e "${HIGHLIGHT}Backing up PostgreSQL database${DEFAULT}"
	mkdir -p $1/postgresql/
	chown postgres $1/postgresql/

	read -p 'Enter database [biobank]: ' database
	database=${database:-biobank}

	tables=( users researchers participants participant_identities participant_subscriptions biobankers studies studies_researchers emails email_recipients )
	for table in "${tables[@]}"
	do
		su -c "psql -U postgres -d $database -c \"COPY ${table} TO '${parent_path}/$1/postgresql/${table}.csv' DELIMITER ',' CSV HEADER;\"" postgres
	done
}

# The WordPress backup creates a CSV file of each WordPress table.
backup_wordpress() {
	echo -e "${HIGHLIGHT}Backing up WordPress database${DEFAULT}"
	mkdir -p $1/wordpress/
	read -p 'Enter database [wordpress]: ' database
	database=${database:-wordpress}
	read -p 'Enter username: ' username
	mysqldump -u $username -p $database > $1/wordpress/wordpress.sql
}

# Update the the ownership of the backup files.
# With the wrong ownership, some backup files would not be copied with `scp`.
change_ownership() {
	if [ $SUDO_USER ]; then
		user=$SUDO_USER
	else
		user=$USER
	fi
	chown -R $user:$user $1/
}

args() {
	options=$(getopt --options oh --long blockchain --long rest --long plugin --long postgresql --long wordpress -- "$@")
	[ $? -eq 0 ] || {
		echo "Unknown option provided"
		usage
		exit 1
	}
	eval set -- "$options"

	len_options=0
	while true; do
        case "$1" in
		-h)
			usage
			;;
        --blockchain)
			backup_fabric $backup
            ;;
        --rest)
			backup_rest $backup
            ;;
        --plugin)
			backup_plugin $backup
            ;;
        --postgresql)
			backup_postgresql $backup
            ;;
        --wordpress)
			backup_wordpress $backup
            ;;
        --)
            shift
            break
            ;;
        esac
        shift
		let len_options++
    done

	if [ $len_options -eq 0 ]
	then
		backup_fabric $backup
		backup_rest $backup
		backup_plugin $backup
		backup_postgresql $backup
		backup_wordpress $backup
	fi
}

backup="$( create_dir $* )"
args $0 "$@"
change_ownership $backup
