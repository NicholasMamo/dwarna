# Dwarna
**Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain**

## Starting Dwarna

To start, Dwarna, execute the `start.sh` script. It might be necessary to make this script executable using `chmod +x start.sh`. The script first starts Hyperledger, and then starts the REST API.

## Directory Structure

More specific `README.md` files are in each of the respective directories where necessary.

### `biobank-plugin/`

The WordPress plugin. It can be installed by placing it in the `wordpress/wp-content/plugins/` directory of your local installation.

### `fabric/`

The Hyperledger Fabric files.

### `rest/`

The REST API, runnable from `rest/main.py`.

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
