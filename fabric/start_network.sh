#!/usr/bin/env bash

# Start the Hyperledger Fabric blockchain and associated REST APIs.

# Set the environment variables.

export COMPOSER_PROVIDERS='{
    "local-wordpress": {
        "provider": "local-wordpress",
        "module": "passport-local-wordpress",
        "authorizationURL": "http://localhost/wordpress/wp-content/plugins/biobank/oauth2/auth.php",
        "tokenURL": "http://localhost/wordpress/wp-content/plugins/biobank/oauth2/access_token.php",
        "userProfileURL": "http://localhost/wordpress/wp-content/plugins/biobank/oauth2/user_profile.php",
        "clientID": "7815696ecbf1c96e6894b779456d330e",
        "clientSecret": "41e0b81ec1d89ccaf238565b50263251",
        "authPath": "/auth/local-wordpress",
        "callbackURL": "/auth/local-wordpress/callback",
        "successRedirect": "http://localhost/wordpress?authorized=true",
        "failureRedirect": "/"
    }
}'

export PATH=~/.npm-global/bin:$PATH
source ~/.nvm/nvm.sh
nvm use 8.9.4

# Start the peer nodes.
cd fabric-scripts/hlfv12/composer/
docker-compose stop
docker-compose start
cd ../../../

# Start the Dwarna network.
cd dwarna-blockchain
composer network install --archiveFile dwarna-blockchain.bna --card PeerAdmin@hlfv1
composer network start --networkName dwarna-blockchain --networkVersion 0.1.0 --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file admin.card
composer card import --file admin.card
cd ..

# Start the multi-user REST API.
composer-rest-server -c admin@dwarna-blockchain -m true >/dev/null 2>&1 &
sleep 5s
multiuser_rest_pid=$!
echo "Multi-user REST API served on port 3000 ($multiuser_rest_pid)"

# Start the administration REST API.
composer-rest-server -c admin@dwarna-blockchain -p 3001 >/dev/null 2>&1 &
sleep 5s
admin_rest_pid=$!
echo "Admin REST API served on port 3001 ($admin_rest_pid)"

sleep 5s
kill -SIGINT $multiuser_rest_pid
kill -SIGINT $admin_rest_pid
