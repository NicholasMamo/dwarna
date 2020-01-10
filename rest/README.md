![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# REST API

The REST API is used as an interface between the frontend (WordPress) and the backend (the database and the blockchain).

## Getting Started

The REST API is an [OAuth2.0](https://tools.ietf.org/html/rfc6749) server based on [python-oauth2](https://github.com/wndhydrnt/python-oauth2).
The REST API uses the [Client Credentials grant](https://tools.ietf.org/html/rfc6749#section-1.3.4).
Resource requests to it are expected to be preceded by a request to obtain an access token.

The REST API itself requires no installation.
However, before using it, you will need to configure it.

### Configuration

The configuration files should be placed in the `config/` directory.
To get started quickly, copy the configuration files from the `config/examples` directory.
Fill the required fields before starting the REST API.
Any time you update the configuration, you will need to restart the REST API.
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

### Starting

The REST API can be run using:

 	chmod +x main.py
	./main.py

Command-line arguments:

* -p --port - The port on which to serve the REST API, defaults to 7225 (optional).

## Deployment

To deploy the project, add the site to `/etc/apache2/sites-available/rest.conf`, or a similar file.
The configuration should look similar to what follows:

```
Listen 7225
<VirtualHost *:7225>
    DocumentRoot /var/www/html/dwarna

    ErrorLog ${APACHE_LOG_DIR}/dwarna_rest_error.log

    WSGIDaemonProcess dwarna python-path=/var/www/html/dwarna/rest/venv/bin:/var/www/html/dwarna/rest/venv/lib/python3.7/site-packages
    WSGIPassAuthorization On
    WSGIProcessGroup dwarna
    WSGIScriptAlias / /var/www/html/dwarna/rest/main.py
</VirtualHost>
```

Activate the site using:

    sudo a2ensite rest

In deployment, the server expects to find a `.pgpass` with the used databases in `/var/www`.

To test that the deployment is working correctly, first get a token:

	curl --request POST \
	--url http://localhost:7225/token \
	--header 'content-type: application/x-www-form-urlencoded' \
	--data grant_type=client_credentials \
	--data client_id=CLIENT_ID \
	--data client_secret=CLIENT_SECRET

Then, ping the server:

	curl -I --request GET \
	--url http://localhost:7225/ping \
	--header 'authorization: ACCESS_TOKEN'

## Running the tests

The unit tests can be run using:

 	chmod +x tests.sh
	./tests.sh

Command-line arguments:

* -t - The test to run, one of _consent_, _general_, _email_, _study_, _user_.

If no argument is given, all tests are run (optional).

## Documentation

The documentation is in the `documentation/build` directory and can be navigated as a normal webpage.
To generate the documentation:

	sphinx-build documentation/source/ documentation/build

## Built with

* [python-oauth2](https://github.com/wndhydrnt/python-oauth2)

## Authors

* **Nicholas Mamo** - *Development* - [NicholasMamo](https://github.com/NicholasMamo)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for this README template
