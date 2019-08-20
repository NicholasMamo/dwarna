![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain

Dwarna ('about us' in Maltese) is a blockchain-based dynamic consent application for biobanking. The application, which is served through a WordPress plugin, uses a Hyperledger Fabric blockchain, through Hyperledger Composer, to store research participants' consent changes. In this way, the blockchain stores an immutable consent trail. The application contains functionality to manage research studies, research participants and researchers in WordPress.

---

## Installing Dwarna

To install, Dwarna, execute the `install.sh` script. It might be necessary to make this script executable using `chmod +x install.sh`. The script installs the schema using psycopg2, and then Hyperledger Fabric and its dependencies.

## Starting Dwarna

To start, Dwarna, execute the `start.sh` script. It might be necessary to make this script executable using `chmod +x start.sh`. The script first starts Hyperledger Fabric, and then starts the REST API.

## Unit Tests

To run the unit tests, execute the `tests.sh` script. It might be necessary to make this script executable using `chmod +x tests.sh`.

### Command-Line Arguments

-t - The test to run, one of _rest_, _schema_. To run the individual tests for each type, run the `tests.sh` scripts in the `rest` and `setup` directories. If no argument is given, all tests are run (optional).

## Directory Structure

More specific `README.md` files are in each of the respective directories where necessary.

### `biobank-plugin/`

The WordPress plugin.

### `fabric/`

The Hyperledger Fabric files.

### `rest/`

The REST API.

### `setup/`

The setup scripts to construct the database schema for the REST API and associated tests.

## Dependencies

- REST API
	- psycopg2
	- python-oauth2
	- requests
	- requests-toolbelt
- Hyperledger Composer
	- docker-compose
