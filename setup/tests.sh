#!/bin/bash

# to allow relative path calls
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path

source ../variables.sh

python3 tests/environment.py

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <email|study|user>]${DEFAULT}";
}

email_tests() {
	echo -e "${HIGHLIGHT}Email Schema Tests${DEFAULT}"
}

study_tests() {
	echo -e "${HIGHLIGHT}Study Schema Tests${DEFAULT}"
	python3 -m unittest tests.test_study_schema
}

user_tests() {
	echo -e "${HIGHLIGHT}User Schema Tests${DEFAULT}"
	python3 -m unittest tests.test_user_schema
}

if getopts "t:" o
then
	case "${OPTARG}" in
		email)
			email_tests
			;;
		study)
			study_tests
			;;
		user)
			user_tests
			;;
		*)
			echo -e "${HIGHLIGHT}Invalid argument${DEFAULT}"
			usage
			;;
	esac
else
	email_tests
	study_tests
	user_tests
fi
