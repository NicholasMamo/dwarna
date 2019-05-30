#!/bin/bash

# to allow relative path calls
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path

source ../variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <user|study|general|consent>]${DEFAULT}";
}

consent_tests() {
	echo -e "${HIGHLIGHT}Consent Tests${DEFAULT}"
	python3 -m unittest tests.test_consent_management
}

user_tests() {
	echo -e "${HIGHLIGHT}User Tests${DEFAULT}"
	python3 -m unittest tests.test_user_management
}

study_tests() {
	echo -e "${HIGHLIGHT}Study Tests${DEFAULT}"
	python3 -m unittest tests.test_study_management
}

general_tests() {
	echo -e "${HIGHLIGHT}General Tests${DEFAULT}"
	python3 -m unittest tests.test_general_functionality
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
		general)
			general_tests
			;;
		consent)
			consent_tests
			;;
		*)
			echo -e "${HIGHLIGHT}Invalid argument${DEFAULT}"
			usage
			;;
	esac
else
	user_tests
	study_tests
	general_tests
	consent_tests
fi
