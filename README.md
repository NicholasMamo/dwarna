# Dwarna
**Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain**

## Starting Dwarna

To start, Dwarna, execute the `start.sh` script. It might be necessary to make this script executable using `chmod +x start.sh`. The script first starts Hyperledger Fabric, and then starts the REST API.

## Installing Dwarna

To install, Dwarna, execute the `install.sh` script. It might be necessary to make this script executable using `chmod +x install.sh`. The script installs Hyperledger Fabric and its dependencies.

## Directory Structure

More specific `README.md` files are in each of the respective directories where necessary.

### `biobank-plugin/`

The WordPress plugin. It can be installed by placing it in the `wordpress/wp-content/plugins/` directory of your local installation.

### `fabric/`

The Hyperledger Fabric files.

### `rest/`

The REST API, runnable from `rest/main.py`.

#### Command-Line Arguments

-p --port - The port on which to serve the REST API, defaults to 7225 (optional).

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
