#!/usr/bin/env bash

# Go to the script's parent directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/.."

source variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path [-h] [pseudonym]...";
	echo -e "       -p path    The path of the backups folder, for example 'backup/20191217'";
	echo -e "       The last arguments are taken to be pseudonyms";
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

