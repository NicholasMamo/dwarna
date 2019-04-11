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

# 1 - to start from scratch
composer card delete --card admin@dwarna-blockchain
./stopFabric.sh
./startFabric.sh
cd dwarna-blockchain/

# 1 - to resume
cd fabric-scripts/hlfv12/composer/
docker-compose stop
docker-compose start
cd ../../../dwarna-blockchain

# start the network
composer network install --archiveFile dwarna-blockchain.bna --card PeerAdmin@hlfv1
composer network start --networkName dwarna-blockchain --networkVersion 0.1.1 --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file admin.card
composer card import --file admin.card

# 2
composer-rest-server -c admin@dwarna-blockchain -m true # user authentication on port 3000

# 3
composer-rest-server -c admin@dwarna-blockchain -p 3001 # admin setup on port 3001

# upgrade network

composer network install --archiveFile dwarna-blockchain.bna --card PeerAdmin@hlfv1
composer network upgrade -c PeerAdmin@hlfv1 -n dwarna-blockchain -V {VERSION}
