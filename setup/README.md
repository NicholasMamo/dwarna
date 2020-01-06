![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Database Setup

The setup scripts are used to construct the database schema that supports Dwarna.
There are two schemas included.
One is for the REST API's OAuth 2.0 implementation, described [here](https://github.com/wndhydrnt/python-oauth2).
The other is for Dwarna's own data.

## Getting Started

### Installing

To set up the schema, run the two setup scripts:

    chmod +x minimal_schema.py
	./minimal_schema.py

	chmod +x oauth_schema.py
	./oauth_schema.py

The two scripts look for a [`~/.pgpass`](https://www.postgresql.org/docs/current/libpq-pgpass.html) file to connect to PostgreSQL initially.
The contents should be of the form `hostname:port:database:username:password`.
By default, the database and OAuth 2.0 scripts look for existing databases with names _biobank_ and _biobank_oauth_.
The databases are not created if they do not exist.

### Prerequisites

Before running the setup script, create the databases.
By default, the database and OAuth 2.0 scripts look for existing databases with names _biobank_ and _biobank_oauth_.
The connection details should be stored in the [`~/.pgpass`](https://www.postgresql.org/docs/current/libpq-pgpass.html).
The contents should be of the form `hostname:port:database:username:password`.

### Running the tests

To run the unit tests, use the `tests.sh` file:

	chmod +x tests.sh
	./tests.sh

The unit testing ensures the correct functioning of Dwarna's database schema.
The project contains unit tests for the study, email and users.
To run them separately, use the `-t` command-line argument:

    ./tests.sh -t email
	./tests.sh -t study
    ./tests.sh -t user

## Built with

* [python-oauth2](https://github.com/wndhydrnt/python-oauth2)

## Authors

* **Nicholas Mamo** - *Development* - [NicholasMamo](https://github.com/NicholasMamo)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for this README template
