#!/bin/bash

# to allow relative path calls
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path

source ../variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <consent|general|study|user>]${DEFAULT}";
}

consent_tests() {
	echo -e "${HIGHLIGHT}Consent Tests${DEFAULT}"
	python3 -m unittest tests.test_consent_management
}

general_tests() {
	echo -e "${HIGHLIGHT}General Tests${DEFAULT}"
	python3 -m unittest tests.test_general_functionality
}

study_tests() {
	echo -e "${HIGHLIGHT}Study Tests${DEFAULT}"
	python3 -m unittest tests.test_study_management
}

user_tests() {
	echo -e "${HIGHLIGHT}User Tests${DEFAULT}"
	python3 -m unittest tests.test_user_management
}

if getopts "t:" o
then
	case "${OPTARG}" in
		consent)
			consent_tests
			;;
		general)
			general_tests
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
	consent_tests
	general_tests
	study_tests
	user_tests
fi
