#!/usr/bin/env bash

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
source $parent_path/../variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path [-h] [pseudonym]...";
	echo -e "       -p path    The path of the backups folder, for example 'backup/20191217'";
	echo -e "       The last arguments are taken to be pseudonyms";
}

# Check if the provided path is a zip file.
is_zip() {
	if [ ${1:(-7)} = '.tar.gz' ]; then
		true
		return
	fi

	false
	return
}

# Unzip the given tar file.
unzip() {
	tar -zxf $1
	echo ${1:0:(-7)}
	return
}

# Zip the backup file to make it easier to store.
zip() {
	tar -zcf "$1.tar.gz" $1
	echo "$1.tar.gz"
	return
}

if [ "$1" == "-p" ]
then
	shift
	path="$1"

	# Remove the trailing slash from the path if given.
	if [ ${path:(-1)} = '/' ]; then
		path=${path:0:(-1)}
	fi
	shift
else
	echo "Expected path option"
	usage
	exit 1
fi

for D in $path/*; do
    if [ -d "${D}" ]; then # if it is a folder, erase normally
		echo -e "${HIGHLIGHT}Erasing $@ from $D${DEFAULT}"
		if [ -d "$D/wordpress" ]; then
        	$parent_path/erase_wordpress.py -p $D -e $@
		fi
		if [ -d "$D/postgresql" ]; then
        	$parent_path/erase_postgresql.py -p $D -e $@
		fi
	elif is_zip $D; then # if it is an archive, extract it, erase the data and re-create the archive
		echo -e "${HIGHLIGHT}Erasing $@ from archive $D${DEFAULT}"
		D="$( unzip $D )"
		if [ -d "$D/wordpress" ]; then
        	$parent_path/erase_wordpress.py -p $D -e $@
		fi
		if [ -d "$D/postgresql" ]; then
        	$parent_path/erase_postgresql.py -p $D -e $@
		fi
		archive="$( zip $D )"
    fi
done
