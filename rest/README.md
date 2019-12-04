![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# REST API

The REST API is used by the WordPress plugin to store biobanking-related information.

## Starting the REST API

The REST API can be run using `python3 main.py`.

### Command-Line Arguments

-p --port - The port on which to serve the REST API, defaults to 7225 (optional).

### Configuration

The configuration files should be placed in the `config/` directory.
Copies of the configuration files are in the `config/examples` directory.
The files in the `config` directory should be the following:

- `blockchain.py` - Information about where the Hyperledger Fabric blockchain is served.
					This includes the ports where the multi-user and administration endpoints of Hyperledger Composer's REST API should be served;
- `db.py` - 		The configuration file with information such as which databases should be used.
					An encryption secret is used to encrypt sensitive personal information;
- `email.py` - 		The email configuration, including SMTP details;
- `oauth.py` - 		The OAuth 2.0 configuration.
 					This includes the lifetime of access tokens and a list of scopes, extracted automatically from the routes.
					The client ID and secret have to be generated anew; and
- `routes.py` - 	The routes served by the REST API, each linked with a handler function.

## Documentation

The documentation is in the `documentation/build` directory and can be navigated as a normal webpage.
To generate the documentation, `cd` to this directory and run:

```bash
	sphinx-build documentation/source/ documentation/build
```

## Unit Tests

The unit tests can be run using `./tests.sh`.
It might be necessary to make this script executable using `chmod +x tests.sh`.

### Command-Line Arguments

-t - The test to run, one of _consent_, _general_, _email_, _study_, _user_.
If no argument is given, all tests are run (optional).
