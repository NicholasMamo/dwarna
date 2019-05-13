#!/usr/bin/env bash

# Start the Hyperledger Fabric blockchain and associated REST APIs.

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
        "successRedirect": "http://localhost/wordpress?authorized=true",
        "failureRedirect": "/"
    }
}'

export PATH=~/.npm-global/bin:$PATH
export FABRIC_VERSION=hlfv12
source ~/.nvm/nvm.sh
nvm use 8.9.4

# Start the peer nodes.
cd fabric-scripts/hlfv12/composer/
docker-compose stop
sleep 15s
docker-compose start
sleep 15s
cd ../../../

# Start the Dwarna network.
cd dwarna-blockchain
composer card delete --card admin@dwarna-blockchain
echo "Installing network"
composer network install --archiveFile dwarna-blockchain.bna --card PeerAdmin@hlfv1
echo "Starting network"
composer network start --networkName dwarna-blockchain --networkVersion 0.1.2 --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file admin@dwarna-blockchain.card
echo "Importing card"
composer card import --file admin@dwarna-blockchain.card --card admin@dwarna-blockchain
cd ..

# Start the multi-user REST API.
composer-rest-server -c admin@dwarna-blockchain -m true &
sleep 10s
multiuser_rest_pid=$!
echo "Multi-user REST API served on port 3000 ($multiuser_rest_pid)"

# Start the administration REST API.
composer-rest-server -c admin@dwarna-blockchain -p 3001 &
sleep 10s
admin_rest_pid=$!
echo "Admin REST API served on port 3001 ($admin_rest_pid)"

composer-playground >/dev/null 2>&1 &
echo "Composer Playground served on port 8080"
