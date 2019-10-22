![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# REST API

The REST API is used by the WordPress plugin to store biobanking-related information.

## Starting the REST API

The REST API can be run using `python3 main.py`.

### Command-Line Arguments

-p --port - The port on which to serve the REST API, defaults to 7225 (optional).

### Configuration

The configuration files are in the `config/` directory. These files contain the following information:

- `blockchain.py` - information about where the Hyperledger Fabric blockchain is served, including the ports where the multi-user and administration endpoints of Hyperledger Composer's REST API should be served;
- `db.example.py` - a shell containing information such as which databases should be used. The file needs to be renamed to `db.py` and filled in. To generate an encryption secret, used to encrypt sensitive personal information of users run the following:
```python
	from cryptography.fernet import Fernet
	key = Fernet.generate_key()
````
- `oauth.py` - the OAuth 2.0 configuration, including the lifetime of access tokens and a list of scopes, extracted automatically from the routes; and
- `routes.py` - the routes served by the REST API, each linked with a handler function.

## Documentation

The documentation is in the `documentation/build` directory and can be navigated as a normal webpage.
To generate the documentation, `cd` to this directory and run:

```bash
	sphinx-build documentation/source/ documentation/build
```

## Unit Tests

The unit tests can be run using `./tests.sh`. It might be necessary to make this script executable using `chmod +x tests.sh`.

### Command-Line Arguments

-t - The test to run, one of _consent_, _general_, _study_, _user_. If no argument is given, all tests are run (optional).
