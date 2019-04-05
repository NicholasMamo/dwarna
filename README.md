# Dwarna
**Dwarna: Introducing a Dynamic Consent Solution for Biobanking on the Blockchain**

## Directory Structure

### `biobank-plugin/`

The WordPress plugin. It can be installed by placing it in the `wordpress/wp-content/plugins/` directory of your local installation.

### `fabric/`

The Hyperledger Fabric files.

### `rest/`

The REST API, runnable from `rest/main.py`.

### `setup/`

The setup scripts to construct the database schema for the REST API and associated tests.

## REST API

Dependencies:

- psycopg2
- python-oauth2
- requests
- requests-toolbelt
