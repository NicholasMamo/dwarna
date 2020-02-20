#!/usr/bin/env bash

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
source $parent_path/../variables.sh

if [ -f $parent_path/cred.conf ]; then
	. $parent_path/cred.conf
fi

# Get the output directory
get_output_dir() {
	output='backup'
	if has_param '-o' $*; then
		output=$(get_param '-o' $*)
	fi
	mkdir -p $output
	echo $output
	return
}

# Create the backup's output directory.
create_dir() {
	backup=$( date +%Y%m%d )
	mkdir -p $1/$backup
	echo "$backup"
}

# Check whether the given parameter is given.
# The function expects first the parameter to look for. Then, it expects the rest of the parameters.
has_param() {
	# Consume the parameter to look for.
	param=$1
	shift

	# Iterate over all the given parameters.
	for ((i=1; i<=$#; i++)); do
		if [ "${!i}" = $param ]; then
			true
			return
		fi
	done
	false
	return
}

# Get the value of the given parameter.
# The function expects first the parameter to look for. Then, it expects the rest of the parameters.
get_param() {
	param=$1
	shift

	for ((i=0; i<$#; i++)); do
		if [ "${!i}" = $param ]; then
			let position="i+1"
			echo ${!position}
			return
		fi
	done
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
		su -c "psql -U postgres -d $database -c \"COPY ${table} TO '/tmp/${table}.csv' DELIMITER ',' CSV HEADER;\"" postgres
		cp /tmp/$table.csv $( pwd )/$1/postgresql/
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
	chown -R $user:$user $1
}

# Zip the backup file to make it easier to store.
zip() {
	tar -zcf "$1.tar.gz" $1
	echo "$1.tar.gz"
	return
}

args() {
	options=$(getopt --options hoz --long blockchain --long rest --long plugin --long postgresql --long wordpress -- "$@")
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
		-o)
			let len_options--
			;;
		-z)
			let len_options--
			;;
        --blockchain)
			backup_fabric $output/$backup
            ;;
        --rest)
			backup_rest $output/$backup
            ;;
        --plugin)
			backup_plugin $output/$backup
            ;;
        --postgresql)
			backup_postgresql $output/$backup
            ;;
        --wordpress)
			backup_wordpress $output/$backup
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
		backup_fabric $output/$backup
		backup_rest $output/$backup
		backup_plugin $output/$backup
		backup_postgresql $output/$backup
		backup_wordpress $output/$backup
	fi
}

output="$( get_output_dir $* )"
backup="$( create_dir $output )"
echo -e "${HIGHLIGHT}Backing up to $output/$backup${DEFAULT}"
args $0 "$@"
change_ownership $output/$backup

# Create an archive of the backup folder if the `z` parameter is given.
zip=$(has_param '-z' $*)
if has_param '-z' $*; then
	echo -e "${HIGHLIGHT}Creating archive $backup.tar.gz${DEFAULT}"
	cd $output
	archive="$( zip $backup )"
	change_ownership $archive
	rm -r $backup
fi
