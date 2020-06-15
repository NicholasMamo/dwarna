![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Hyperledger Fabric

A Hyperledger Fabric blockchain is used to store information about research partners' consent changes.
Hyperledger Composer is used to facilitate development.

## Getting Started

### Prerequisites

Before installing the Dwarna blockchain, install the [Hyperledger Composer developer tools](https://hyperledger.github.io/composer/latest/installing/development-tools.html).
Other prerequisites are installed in the `install_network.sh` script.

### Installing

To install the Dwarna blockchain and related prerequisites, run the `install_network.sh` script:

	./install_network.sh

The script first installs NVM and the necessary NPM modules.
Then, it installs prerequisites for the Hyperledger blockchain, downloads Hyperledger Fabric and creates a Peer Admin card.
The script also deletes any existing Dwarna administrator cards.
Finally, it stops and starts Hyperledger Fabric to set up any necessary configurations.

You can start the Dwarna network using the `start_network.sh` script.
Create `start_network.sh` by copying `start_network.example.sh` and filling in the `clientID` and `clientSecret`.
Use the OAuth 2.0 values retrieved by following the process when installing the [WordPress plugin](https://github.com/NicholasMamo/dwarna/tree/master/biobank-plugin).
Then run the new script normally:

	./start_network.sh

The script configures Hyperledger Composer to use the custom-made Passport.js.
Then it restarts the Docker containers to start Hyperledger Fabric.
Subsequently, it installs and starts the Dwarna network, importing the Dwarna administrator card.

The script also starts two different REST APIs.
The first one is the administrator REST API
The second one is the multi-user REST API.
Finally, the script launches Composer Playground.

### Reinstalling

To recreate the Dwarna blockchain from scratch:

	./reinstall_network.sh

The script stops Hyperledger Fabric, tears down all Docker images, downloads them anew and starts up the blockchain again.
Note that this removes all data and should be accompanied by a clean install of the databases to avoid zombie users.

The process will currently fail to complete if the backup folders exist.
The data is still erased, but there will be inconsistencies left that keep the blockchain from starting.

### Upgrading

To upgrade the blockchain with a new version of the Dwarna network:

* `cd` to `dwarna-blockchain` directory and place the new `dwarna-blockchain` file in the it;
* run the command `composer network upgrade -c PeerAdmin@hlfv1 -n dwarna-blockchain -V {VERSION}`, replacing `{VERSION}` with the new version number; and
* update the `start_network.sh` script, similarly updating the version number in the following line:

		composer network start --networkName dwarna-blockchain \
		--networkVersion {VERSION} --networkAdmin admin \
		--networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 \
		--file admin@dwarna-blockchain.card

## Backups

Dwarna stores backups as volumes from the Docker images.
The volumes are stored in the `fabric-scripts/hlfv12/composer/backup_*` directories.
These directories are mounted automatically when the images start.
The roles of these volumes are as follows:

* `backup_ca_server` - the volume from the certificate authority service, stores the users that are known to it—necessary to re-use the administator card;
* `backup_orderer` - the volume from the orderer node; and
* `backup_peer` - the volume from the peer, stores the ledger data.

Apart from these volumes, the administrator card needs to be re-used.
Dwarna looks for this card in the `dwarna-blockchain` directory.

### Restoring Backups

To restore backups:

* remove the `fabric-scripts/hlfv12/composer/backup_*` directories as well as the `dwarna-blockchain/admin@dwarna-blockchain.card`;
* run the `reinstall_network.sh` script;
* copy the `backup_*` folders to the `fabric-scripts/hlfv12/composer/` directory;
* copy `admin@dwarna-blockchain.card` to the `dwarna-blockchain` directory; and
* start the network normally by running `./start_network.sh`

## Passport

To authenticate users, Dwarna uses a custom [Passport.js](https://github.com/jaredhanson/passport) strategy.
The strategy checks only whether the user has logged in to WordPress, and authenticates them.

The passport files are located in `node/passport-local-wordpress`.
Most changes will need to be made to the `lib/strategy.js` file.
To install, first export the NPM global path and set the NPM prefix.
Then, install globally, which saves the files in the specified directory:

	npm config set prefix '~/.npm-global'
	export PATH=~/npm-global/bin:$PATH
	npm install -g node/passport-local-wordpress/

Any debugging is printed in the same terminal as where the network is started.
To debug the OAuth2 passport scheme, use the files in the `node/passport-local-wordpress/node_modules/passport-oauth2/` directory.

## Built with

* [Passport.js](https://github.com/jaredhanson/passport)

## Authors

* **Nicholas Mamo** - *Development* - [NicholasMamo](https://github.com/NicholasMamo)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for this README template
