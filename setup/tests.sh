#!/bin/bash

# to allow relative path calls
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path

source ../variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <user|study>]${DEFAULT}";
}

user_tests() {
	echo -e "${HIGHLIGHT}User Schema Tests${DEFAULT}"
	python3 -m unittest tests.test_user_schema
}

study_tests() {
	echo -e "${HIGHLIGHT}Study Schema Tests${DEFAULT}"
	python3 -m unittest tests.test_study_schema
}

if getopts "t:" o
then
	case "${OPTARG}" in
		user)
			user_tests
			;;
		study)
			study_tests
			;;
		*)
			echo -e "${HIGHLIGHT}Invalid argument${DEFAULT}"
			usage
			;;
	esac
else
	user_tests
	study_tests
fi
