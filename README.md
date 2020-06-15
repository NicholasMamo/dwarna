![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Dwarna: A Blockchain Solution for Dynamic Consent in Biobanking

Dwarna ('about us' in Maltese) is a blockchain-based dynamic consent application for biobanking.
In biobanking, individuals provide biospecimens, like blood or saliva, to be used in medical research.
Dynamic consent transforms these individuals into research partners, allowing them to decide in which research they want to participate.
Dwarna is an application that is served through a WordPress plugin.
It uses a Hyperledger Fabric blockchain to store research partners' consent changes to create an immutable consent trail.

More details about Dwarna can be found in [Dwarna: A Blockchain Solution for Dynamic Consent in Biobanking](https://www.nature.com/articles/s41431-019-0560-9), published in the European Journal of Human Genetics.

## Getting Started

To download this repository, clone it using `git clone https://github.com/NicholasMamo/dwarna.git`.
Then, follow the installation instructions in this README file.
This repository contains three different sub-projects: a WordPress plugin, a Hyperledger Fabric blockchain and a REST API.
More detailed instructions about each sub-project, including installation and configuration instructions, are in the respective directories:

- [WordPress biobank plugin README.md](https://github.com/NicholasMamo/dwarna/tree/master/biobank-plugin)
- [Hyperledger Fabric README.md](https://github.com/NicholasMamo/dwarna/tree/master/fabric)
- [REST API README.md](https://github.com/NicholasMamo/dwarna/tree/master/rest)

### Prerequisites

Details about the prerequisites are available in each README.md file.
Some Python prerequisites are required to run the REST API and the setup scripts:

    virtualenv venv
	source venv/bin/activate
	python -m pip install -r requirements.txt

### Installing

To install Dwarna, use the `install.sh` script:

	./install.sh

The script installs the schema using psycopg2, and Hyperledger Fabric and its dependencies.

However, you still need to configure the REST API and the WordPress plugin.
To do this, follow the README files above.

Once you have configured Dwarna, you can start Hyperledger Composer and the REST API using the `start.sh` script:

	./start.sh

The email delivery script is part of the REST API.
To run it:

    ./rest/deliver.py

### Backups

Dwarna's `tools/backup.sh` script takes a backup of all the files that are necessary to restore all data.
To take a backup:

    ./tools/backup.sh

By default, the backups are created in the `backups/` directory.
You can change the destination by using the `-o` argument.
If the `-z` argument is given, an archive is created from the backup.

	./tools/backup.sh -o other/folder -z

Backups are separated into folders according to the date when they were taken.
These directories have the format `yyyymmdd`.
Each backup is further separated into folders:

* `fabric/` - The blockchain data;
* `rest/` - The REST API configuration;
* `biobank-plugin/` - The WordPress plugin configuration;
* `postgresql/` - The PostgreSQL data; and
* `wordpress/` - The WordPress MySQL data

By default, the backup copies all of this data.
You can specify which data to back up by passing on the following arguments:

* `--blockchain` - Back up only the Hyperledger Fabric files;
* `--rest` - Back up only the REST API configuration;
* `--plugin` - Back up only the WordPress plugin configuration;
* `--postgresql` - Back up only the PostgreSQL data; and
* `--wordpress` - Back up only the WordPress MySQL data

To automate backups, copy the `tools/cred.example.conf` file and fill it in.
The `backup.sh` script automatically reads the credentials from it.

To restore a backup, run the `tools/restore.sh` script:

    ./tools/restore.sh -p backup/yyyymmdd

The script automatically restores the backup stored in the folder named `backup/yyyymmdd`.
If an archive is given instead, the script automatically extracts it.
By default, the restoration copies back all of this data.
You can specify which data to restore by passing on the following arguments:

* `--blockchain` - Restore only the Hyperledger Fabric files;
* `--rest` - Restore only the REST API configuration;
* `--plugin` - Restore only the WordPress plugin configuration;
* `--postgresql` - Restore only the PostgreSQL data; and
* `--wordpress` - Restore only the WordPress MySQL data

### Data erasure

The 'tools/erase.sh' script can be used to erase research partner data from backups, including archives.
The script takes in a path to the directory where backups are stored, and a list of research partner pseudonyms to erase:

	./tools/erase.sh -p backup p2320 p2321

See [REST API README.md](https://github.com/NicholasMamo/dwarna/tree/master/rest) for instructions to erase research partners from backups on deletion.

## CRON

CRON files are available in the `cron` directory.
The scripts are made to be callable directly and automatically log to a file.
Note that the scripts still need to be updated with the correct paths.
Some directories and files need to be created in advance with the correct permissions.

## Running the tests

To run the unit tests, use the `tests.sh` script:

	./tests.sh

The unit testing ensures the correct functioning of the database schema and the REST API.
To run them separately, use the `-t` command-line argument:

    ./tests.sh -t rest
    ./tests.sh -t schema

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/NicholasMamo/dwarna/tags).

## Authors

* **Nicholas Mamo** - *Development* - [NicholasMamo](https://github.com/NicholasMamo)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for this README template
