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
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
cd "$parent_path" # go to the script path
cp -r tests/blockchain tests/test_blockchain
geth --datadir tests/test_blockchain/data/ init tests/test_blockchain/init.json
geth --datadir tests/test_blockchain/data \
	--ipcpath geth01 --nodiscover --networkid 1234 \
	--rpc --rpccorsdomain "*" --rpcapi "db,personal,eth,net,web3,debug,miner" >/dev/null 2>&1 &
blockchain_pid=$!
python3 tests/test_blockchain/start.py

sleep 2s # sleep to allow some mining

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
python3 tests/test_blockchain/shutdown.py
kill $blockchain_pid
rm -r tests/test_blockchain
