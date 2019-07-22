![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Hyperledger Fabric

## Installing Hyperledger Fabric

To install the Dwarna blockchain, `cd` to this directory and execute the `install_network.sh` script. It might be necessary to make this script - and any other scripts that it references - executable using `chmod +x install_network.sh`.

The script first installs NVM and the necessary NPM modules. Then, it installs prerequisites for the Hyperledger blockchain, downloads Hyperledger Fabric and creates a Peer Admin card. The script also deletes any existing Dwarna administrator cards. Finally, it stops and starts Hyperledger Fabric to set up any necessary configurations.

## Starting Hyperledger Fabric

To start Hyperledger Fabric and the Dwarna network, `cd` to this directory and execute the `start_network.sh` script. It might be necessary to make this script - and any other scripts that it references - executable using `chmod +x start_network.sh`.

The script first attaches the custom-made Passport.js to Hyperledger Composer. Then it stops and starts the Docker containers to start Hyperledger Fabric. Subsequently, it installs and starts the Dwarna blockchain, importing the Dwarna administrator card.

The script also starts two different REST APIs. One is the administrator REST API, and the other is the multi-user REST API. Finally, the script launches Composer Playground.

## Reinstalling Hyperledger Fabric

Sometimes, it may be necessary to recreate the Dwarna blockchain. To do this, `cd` to this directory and execute the `reinstall_network.sh` script. It might be necessary to make this script - and any other scripts that it references -  executable using `chmod +x reinstall_network.sh`.

The script stops Hyperledger Fabric, tears down all Docker images, downloads them anew and starts up the blockchain again. The process will currently fail to complete if the backup folders exist. However, in this case, the Hyperledger Fabric blockchain would still be created from scratch.

## Upgrading the Blockchain

To upgrade the blockchain, `cd` to `dwarna-blockchain` directory and place the new file in the it. Then, run the command `composer network upgrade -c PeerAdmin@hlfv1 -n dwarna-blockchain -V {VERSION}`, replacing `{VERSION}` with the new version number. Finally, update the `start_network.sh` script, similarly updating the version number in the following line:

    composer network start --networkName dwarna-blockchain --networkVersion {VERSION} --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file admin@dwarna-blockchain.card

## Backups

Dwarna stores backups as volumes from the Docker images. The volumes are stored in the `fabric-scripts/hlfv12/composer/backup_*` directories. These directories are mounted automatically when the images start. The roles of these volumes are as follows:

- `backup_ca_server` - the volume from the certificate authority service, stores the users that are known to it - necessary to re-use the administator card;
- `backup_orderer` - the volume from the orderer node; and
- `backup_peer` - the volume from the peer, stores the ledger data.

Apart from these volumes, the administrator card needs to be re-used. Dwarna looks for this card in the `dwarna-blockchain` directory.

## Passport

The passport files are located in `node/passport-local-wordpress`.
Most changes will need to be made to the `lib/strategy.js` file.
To install, first export the NPM global path and set the NPM prefix.
Then, install globally, which saves the files in the specified directory.

	npm config set prefix '~/.npm-global'
	export PATH=~/npm-global/bin:$PATH
	npm install -g node/passport-local-wordpress/

Any debugging is printed in the same terminal as where the network is started.
To debug the OAuth2 passport scheme, use the files in the `node/passport-local-wordpress/node_modules/passport-oauth2/` directory.
