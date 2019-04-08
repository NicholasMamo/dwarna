#!/bin/bash

usage() {
	echo "Usage: sh $0 [-t <user|study|general|consent>]";
}

consent_tests() {
	echo "=========="
	echo "Consent Tests"
	echo "=========="
	python3 -m unittest tests.test_consent_management
}

user_tests() {
	echo "=========="
	echo "User Tests"
	echo "=========="
	python3 -m unittest tests.test_user_management
}

study_tests() {
	echo "=========="
	echo "Study Tests"
	echo "=========="
	python3 -m unittest tests.test_study_management
}

general_tests() {
	echo "=========="
	echo "General Tests"
	echo "=========="
	python3 -m unittest tests.test_general_functionality
}

# to allow relative path calls
# parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
# cd "$parent_path" # go to the script path

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
			echo "Invalid argument"
			usage
			;;
	esac
else
	user_tests
	study_tests
	general_tests
	consent_tests
fi

# clean up
# kill $blockchain_pid
