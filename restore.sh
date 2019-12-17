#!/usr/bin/env bash

source variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path";
	echo -e "       -p path    The path of the backup to restore, for example 'backup/20191217'";
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
function restore_wordpress() {
	echo -e "${HIGHLIGHT}Restoring WordPress database${DEFAULT}"
	read -p 'Enter database [wordpress]: ' database
	database=${database:-wordpress}
	read -p 'Enter username: ' username
	mysql -u $username -p $database < $1/wordpress/wordpress.sql
}

if getopts "p:" o
then
	path=${OPTARG}
	restore_plugin $path
	restore_postgresql $path
	restore_wordpress $path
else
	usage
fi
