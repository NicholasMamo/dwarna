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
3. Create a [FontAwesome](https://fontawesome.com/) account to get an icon kit.
   These icons are used by the plugin to beautify it.
   Once you get an icon kit, replace the `$fontawesome_kit` variable's value with a link to the kit.
4. Copy the `public/js/hyperledger/card.example.js` file into `public/js/hyperledger/card.js`.
   Update the variables as need be to point to the Hyperledger Composer REST API endpoints.

To authenticate users against Hyperledger Composer, the plugin uses OAuth 2.0 (separate from the REST API).
This workflow is also tied with the Hyperledger Fabric blockchain.
To configure the OAuth 2.0 server:

1. Generate a client ID and secret by running `php -f oauth2/generate_credentials.php`;
2. Copy the client ID and secret into the `fabric/start_network.sh` script's `clientID` and `clientSecret` fields; and
3. Run the SQL instructions available in `oauth2/install.sql` in the WordPress database that you are using.
   The last line allows you to create the client using the generated client ID and secret.
   Update the client ID and secret.
   Also update the URL to be the same as the callback URL in the `fabric/start_network.sh` script.
4. Update `includes/global.php`'s Oauth 2.0 configuration to point to this database.
   If you are using a proxy to connect to the Hyperledger Composer multi-user REST API, update the proxy settings.
   For example, if you are using `/fabric` as a proxy to port `:3000`, set `proxy_from` to `:3000` and `proxy_to` to `/fabric`.
   This proxy is used as string replacement in `oauth/auth.php` and `oauth/access_token.php`.
   Thus, it may be necessary to make the path more specific.
5. Set the base path of the website for the OAuth 2.0 procedure in `includes/global.php`.
   If you are serving the WordPress blog from _example.com_, leave this empty.
   If you are serving the blog from _example.com/wordpress_, then the base path should be `wordpress`.

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
