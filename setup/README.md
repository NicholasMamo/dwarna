![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Setup

The setup scripts are used to construct the database schema that supports Dwarna.

To install the database schema, use `./minimal_schema.py`. It might be necessary to make this script executable using `chmod +x minimal_schema.py`. Similarly, to install the OAuth 2.0 schema, use `./oauth_schema.py`. It might be necessary to make this script executable using `chmod +x oauth_schema.py`.

The two scripts look for a [`~/.pgpass`](https://www.postgresql.org/docs/current/libpq-pgpass.html) file to connect to PostgreSQL initially. The contents should be of the form `hostname:port:database:username:password
`. By default, the database and OAuth 2.0 scripts look for existing databases with names _biobank_ and _biobank_oauth_. The databases are not created if they do not exist so that they do not overwrite existing data.

## Unit Tests

The unit tests can be run using `./tests.sh`. It might be necessary to make this script executable using `chmod +x tests.sh`.

### Command-Line Arguments

-t - The test to run, one of _study_, _user_. If no argument is given, all tests are run (optional).
