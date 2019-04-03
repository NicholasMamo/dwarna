#!/usr/bin/env bash

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# Get the card name.
extension_pos=`expr index $1 .`-1
card_name=$1
name=${card_name:0:$extension_pos}

# Clean up.
composer card delete -c "$name@dwarna-blockchain"

# Import the card.
composer card import -f "cards/$card_name" -c "$name@dwarna-blockchain"

# Start the server.
composer-rest-server -c "$name@dwarna-blockchain" -p $2

exit 0
