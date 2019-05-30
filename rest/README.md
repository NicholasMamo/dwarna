![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# REST API

The REST API is used by the WordPress plugin to store biobanking-related information.

## Starting the REST API

The REST API can be run using `python3 rest/main.py`.

### Command-Line Arguments

-p --port - The port on which to serve the REST API, defaults to 7225 (optional).

## Unit Tests

The unit tests can be run using `./tests.sh`. It might be necessary to make this script executable using `chmod +x tests.sh`.

### Command-Line Arguments

-t - The test to run, one of _consent_, _general_, _study_, _user_. If no argument is given, all tests are run (optional).
