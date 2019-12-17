#!/usr/bin/env bash

source variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path";
	echo -e "       -p path    The path of the backup to restore, for example 'backup/20191217'";
}

# Restore the WordPress database.
function restore_wordpress() {
	echo -e "${HIGHLIGHT}Restoring WordPress database${DEFAULT}"
	mkdir -p backup/$1/wordpress/
	read -p 'Enter database [wordpress]: ' database
	database=${database:-wordpress}
	read -p 'Enter username: ' username
	mysql -u $username -p $database < $1/wordpress/wordpress.sql
}

if getopts "p:" o
then
	path=${OPTARG}
	restore_wordpress $path
else
	usage
fi
