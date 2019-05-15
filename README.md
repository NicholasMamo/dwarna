# Dwarna
**Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain**

## Starting Dwarna

To start, Dwarna, execute the `start.sh` script. It might be necessary to make this script executable using `chmod +x start.sh`. The script first starts Hyperledger Fabric, and then starts the REST API.

## Installing Dwarna

To install, Dwarna, execute the `install.sh` script. It might be necessary to make this script executable using `chmod +x install.sh`. The script installs Hyperledger Fabric and its dependencies.

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
