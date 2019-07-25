#!/usr/bin/env bash

# Start the Hyperledger Fabric blockchain and associated REST APIs.

# Go to the script directory.
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source ../variables.sh

# Set the environment variables.
export COMPOSER_PROVIDERS='{
    "local-wordpress": {
        "provider": "local-wordpress",
        "module": "passport-local-wordpress",
        "authorizationURL": "http://localhost/wordpress/wp-content/plugins/biobank-plugin/oauth2/auth.php",
        "tokenURL": "http://localhost/wordpress/wp-content/plugins/biobank-plugin/oauth2/access_token.php",
        "userProfileURL": "http://localhost/wordpress/wp-content/plugins/biobank-plugin/oauth2/user_profile.php",
        "clientID": "7815696ecbf1c96e6894b779456d330e",
        "clientSecret": "41e0b81ec1d89ccaf238565b50263251",
        "authPath": "/auth/local-wordpress",
        "callbackURL": "/auth/local-wordpress/callback",
        "successRedirect": "http://localhost/wordpress/biobank-study?authorized=true&action=consent",
        "failureRedirect": "/"
    }
}'

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12
source ~/.nvm/nvm.sh
nvm use 8.9.4

echo -e "${HIGHLIGHT}Starting Hyperledger Fabric${DEFAULT}"
cd fabric-scripts/hlfv12/composer/
docker-compose stop
sleep 15s
docker-compose start
sleep 15s
cd ../../../

echo -e "${HIGHLIGHT}Cleaning Dwarna blockchain${DEFAULT}"
cd dwarna-blockchain
composer card delete --card admin@dwarna-blockchain
echo -e "${HIGHLIGHT}Installing Dwarna blockchain${DEFAULT}"
composer network install --archiveFile dwarna-blockchain.bna --card PeerAdmin@hlfv1
echo -e "${HIGHLIGHT}Starting Dwarna blockchain${DEFAULT}"
composer network start --networkName dwarna-blockchain --networkVersion 0.1.3 --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file admin@dwarna-blockchain.card
echo -e "${HIGHLIGHT}Importing and re-exporting administrator card${DEFAULT}"
composer card import --file admin@dwarna-blockchain.card --card admin@dwarna-blockchain
composer network ping -c admin@dwarna-blockchain
composer card export -c admin@dwarna-blockchain
cd ..

echo -e "${HIGHLIGHT}Starting multi-user Hyperledger Composer REST API${DEFAULT}"
composer-rest-server -c admin@dwarna-blockchain -m true &
sleep 10s
multiuser_rest_pid=$!
echo -e "${HIGHLIGHT}Multi-user REST API served on port 3000 ($multiuser_rest_pid)${DEFAULT}"

echo -e "${HIGHLIGHT}Starting administrator Hyperledger Composer REST API${DEFAULT}"
composer-rest-server -c admin@dwarna-blockchain -p 3001 &
sleep 10s
admin_rest_pid=$!
echo -e "${HIGHLIGHT}Admin REST API served on port 3001 ($admin_rest_pid)${DEFAULT}"

echo -e "${HIGHLIGHT}Starting Composer Playground${DEFAULT}"
composer-playground >/dev/null 2>&1 &
echo -e "${HIGHLIGHT}Composer Playground served on port 8080${DEFAULT}"
