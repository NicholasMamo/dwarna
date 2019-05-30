#!/usr/bin/env bash

# Start all the components of Dwarna

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <rest|schema>]${DEFAULT}";
}

schema_tests() {
	echo -e "${HIGHLIGHT}Schema Tests${DEFAULT}"
	./setup/tests.sh
}

rest_tests() {
	echo -e "${HIGHLIGHT}REST API Tests${DEFAULT}"
	./rest/tests.sh
}

if getopts "t:" o
then
	case "${OPTARG}" in
		schema)
			schema_tests
			;;
		rest)
			rest_tests
			;;
		*)
			echo -e "${HIGHLIGHT}Invalid argument${DEFAULT}"
			usage
			;;
	esac
else
	rest_tests
	schema_tests
fi
