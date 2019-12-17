#!/usr/bin/env bash

source variables.sh

function usage() {
	echo -e "Usage: sh $0 -p path";
	echo -e "       -p path    The path of the backup to restore, for example 'backup/20191217'";
}

if getopts "p:" o
then
	path=${OPTARG}
else
	usage
fi
