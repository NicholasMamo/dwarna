#!/usr/bin/env bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

source variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path [-h] [--blockchain] [--rest] [--plugin] [--postgresql] [--wordpress]";
	echo -e "       -p path    The path of the backup to restore, for example 'backup/20191217'";
}

# Unzip the tar file before restoring the backup.
unzip() {
	tar -zxvf $1
}

# Restore Hyperledger Fabric's admin card and the actual data.
restore_fabric() {
	echo -e "${HIGHLIGHT}Restoring Hyperledger Fabric files${DEFAULT}"
	cp $1/fabric/dwarna-blockchain/admin@dwarna-blockchain.card fabric/dwarna-blockchain/admin@dwarna-blockchain.card
	cp -r $1/fabric/fabric-scripts/hlfv12/composer/* fabric/fabric-scripts/hlfv12/composer/
}

# Restore the REST API's configuration, including the encryption keys.
restore_rest() {
	echo -e "${HIGHLIGHT}Restoring REST API files${DEFAULT}"
	cp $1/rest/config/* rest/config
}

# Restore the WordPress plugin's configuration, including the encryption key.
restore_plugin() {
	echo -e "${HIGHLIGHT}Restoring WordPress plugin files${DEFAULT}"
	cp $1/biobank-plugin/includes/globals.php biobank-plugin/includes/globals.php
}

# Restore the PostgreSQL database.
restore_postgresql() {
	echo -e "${HIGHLIGHT}Restoring PostgreSQL database${DEFAULT}"
	read -p 'Enter database [biobank]: ' database
	database=${database:-biobank}

	parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

	tables=( users researchers participants participant_identities participant_subscriptions biobankers studies studies_researchers emails email_recipients )
	for table in "${tables[@]}"
	do
		su -c "psql -U postgres -d $database -c \"COPY $table FROM '$parent_path/$1/postgresql/$table.csv' DELIMITER ',' CSV HEADER;\"" postgres
	done
}

# Restore the WordPress database.
restore_wordpress() {
	echo -e "${HIGHLIGHT}Restoring WordPress database${DEFAULT}"
	read -p 'Enter database [wordpress]: ' database
	database=${database:-wordpress}
	read -p 'Enter username: ' username
	mysql -u $username -p $database < $1/wordpress/wordpress.sql
}

args() {
	shift
	if [ "$1" == "-p" ]
	then
		shift
		path="$1"
	else
		echo "Expected path option"
		usage
		exit 1
	fi

	options=$(getopt --options h --long blockchain --long rest --long plugin --long postgresql --long wordpress -- "$@")
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
			restore_fabric $path
            ;;
        --rest)
			restore_rest $path
            ;;
        --plugin)
			restore_plugin $path
            ;;
        --postgresql)
			restore_postgresql $path
            ;;
        --wordpress)
			restore_wordpress $path
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
		restore_fabric $path
		restore_rest $path
		restore_plugin $path
		restore_postgresql $path
		restore_wordpress $path
	fi
}

args $0 "$@"
