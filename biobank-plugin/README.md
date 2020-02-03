![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# Dwarna WordPress Plugin

The WordPress plugin that handles all biobanking functionality in the frontend.
The plugin provides functionality to manage researchers, research partners and studies.
It also handles all requests to the REST API.

## Getting Started

The WordPress plugin is an easy-to-use interface to enable dynamic consent.
To get started, follow the installation instructions in this README.md file.

Dwarna's plugin adds three new user roles:

* `biobanker`, synonymous to the administrator, and currently not used;
* `researcher`, who can be added to studies, and view information about the studies they are linked with; and
* `participant`, or a research partner, who can dynamically alter their consent and their email preferences

Each user role has associated with it a list of WordPress capabilities.
Moreover, they also have a list of scopes, which define the kind of data they can request from the REST API.

Once activated, the plugin automatically generates four pages:

* A page that allows users to indicate their interest in becoming research partners;
* A page that allows logged-in research partners to update their email subscription preferences;
* A page that shows a list of ongoing research studies; and
* A page that shows a single study, alongside the consent trail of the research partner

The plugin also adds a few shortcodes that can be placed anywhere:

* `[biobank-consent]` to show the consent form;
* `[biobank-recruitment]` to show the recruitment form;
* `[biobank-study]` to show a study;
* `[biobank-subscription]` to show the email subscription preferences form; and
* `[biobank-trail]` to show the consent trail

### Prerequisites

The plugin has been developed for WordPress 5.0.

### Configuration

Before installing and using the plugin, set up the configuration.
To configure the plugin:

1. Copy the `includes/globals.example.php` file into `includes/globals.php`;
2. Fill in the `ENCRYPTION_KEY` constant.
   First generate a key using `php -r "echo bin2hex(sodium_crypto_secretbox_keygen());" > itop_secret_key.txt`.
   Then, replace the 'x' string in the `ENCRYPTION_KEY` constant with the contents of the new `itop_secret_key.txt`; and
3. Copy the `public/js/hyperledger/config.example.js` file into `public/js/hyperledger/config.js`.
   Update the variables as need be to point to the Hyperledger Composer multi-user REST API endpoint.

To authenticate users against Hyperledger Composer, the plugin uses OAuth 2.0 (separate from the REST API).
This workflow is also tied with the Hyperledger Fabric blockchain.
To configure the OAuth 2.0 server:

1. Generate a client ID and secret by running `php -f oauth2/generate_credentials.php`;
2. Copy the client ID and secret into the `fabric/start_network.sh` script's `clientID` and `clientSecret` fields; and
3. Run the last SQL instruction available in `oauth2/install.sql` in the WordPress database that you are using.
   This last line allows you to create the client using the generated client ID and secret.
   Before running, update the client ID and secret, as well as the URL to be the same as the callback URL in the `fabric/start_network.sh` script.
   All the other commands are run upon activation.
4. Update `includes/global.php`'s OAuth 2.0 configuration to point to this database.
5. Update `includes/global.php`'s SMTP details.
   These settings are used to send emails related to the plugin.

After activating the plugin, you may need to complete some other configuration options.
The configuration can be accessed from the _Biobank_ menu.
This menu is created automatically upon activation, and includes a _Settings_ page.
From this page, you can update the configuration for the REST API, the Hyperledger Composer connection and other details:

1. If need be, update the hosting details of the REST API.
   You will need to input the client ID and secret.
   You can retrieve these from the `rest/oauth.py` file after following the [REST API installation instructions](https://github.com/NicholasMamo/dwarna/tree/master/rest).
2. If you are using a proxy to connect to the Hyperledger Composer multi-user REST API, update the proxy settings.
   For example, if you are using `/fabric` as a proxy to port `:3000`, set `proxy_from` to `:3000` and `proxy_to` to `/fabric`.
   This proxy is used as string replacement in `oauth/auth.php` and `oauth/access_token.php`.
   It may be necessary to make the path more specific.
3. Set the base path of the WordPress website for the OAuth 2.0 procedure.
   If you are serving the WordPress blog from _example.com_, leave this empty.
   If you are serving the blog from _example.com/wordpress_, then the base path should be `wordpress`.
4. Fill in the path to the `get_cookie.php` script.
   This file is served using WordPress and is located at `biobank-plugin/public/ajax/get_cookie.php`.
   This needs to be updated especially when Hyperledger Composer and the actual WordPress blog are served on different servers.
   If they are separate, you would need to update the URL to link to this script on the Hyperledger Composer server.
5. Fill in the authentication URL to where the Hyperledger Composer multi-user REST API is being served.
   This URL should match the one set in the `fabric/start_network.sh` script as `authPath`.
   Nevertheless, the server host should be updated if the Hyperledger Composer multi-user REST API is being served from a different server than the WordPress blog.
6. Create a [FontAwesome](https://fontawesome.com/) account to get an icon kit.
   These icons are used by the plugin to beautify it.
   Once you get an icon kit, replace the FontAwesome kit URL with a link to the newly-created kit.

### Activating

To activate the plugin, place this directory in the `wordpress/wp-content/plugins/` directory of your local installation.
Alternatively, create a shortcut (or symbolic link) to this directory in the `wordpress/wp-content/plugins/` folder.
Then, navigate to the _Installed Plugins_ tab under the _Plugins_ menu and activate the `Dwarna` plugin.

### Deactivating

To deactivate the plugin, navigate to the _Installed Plugins_ tab under the _Plugins_ menu and press the _Deactivate_ link under the plugin.
This cleans the database from the plugin's data, and removes the automatically-generated pages.

### Uninstalling

To uninstall and remove the plugin, navigate to the _Installed Plugins_ tab under the _Plugins_ menu, press the _Deactivate_ link under the plugin, and then press the _Remove_ link under the plugin.
This cleans the database from the plugin's data, removes the automatically-generated pages, and removes the plugin files.

## Built with

* [WordPress-Plugin-Boilerplate](https://github.com/devinvinson/WordPress-Plugin-Boilerplate/)

## Authors

* **Nicholas Mamo** - *Development* - [NicholasMamo](https://github.com/NicholasMamo)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for this README template
