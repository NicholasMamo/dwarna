#!/bin/bash

# to allow relative path calls
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path

source ../variables.sh

usage() {
	echo -e "${HIGHLIGHT}Usage: sh $0 [-t <card|consent|email|general|study|user>]${DEFAULT}";
}

card_tests() {
	echo -e "${HIGHLIGHT}Consent Tests${DEFAULT}"
	python3 -m unittest tests.test_card_modes
}

consent_tests() {
	echo -e "${HIGHLIGHT}Consent Tests${DEFAULT}"
	python3 -m unittest tests.test_consent_management
}

email_tests() {
	echo -e "${HIGHLIGHT}Email Tests${DEFAULT}"
	python3 -m unittest tests.test_email_management
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
		card)
			card_tests
			;;
		consent)
			consent_tests
			;;
		email)
			email_tests
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
	card_tests
	consent_tests
	email_tests
	general_tests
	study_tests
	user_tests
fi
