![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain

## Starting Dwarna

To start, Dwarna, execute the `start.sh` script. It might be necessary to make this script executable using `chmod +x start.sh`. The script first starts Hyperledger Fabric, and then starts the REST API.

## Installing Dwarna

To install, Dwarna, execute the `install.sh` script. It might be necessary to make this script executable using `chmod +x install.sh`. The script installs the schema using psycopg2, and then Hyperledger Fabric and its dependencies.

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
- Hyperledger Fabric
	- docker-compose
