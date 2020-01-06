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
2. Fill in the `$encryptionKey` variable.
   First generate a key using `php -r "echo bin2hex(sodium_crypto_secretbox_keygen());" > itop_secret_key.txt`.
   Then, replace the 'x' string in the `$encryptionKey` variable with the contents of the new `itop_secret_key.txt`.
3. Create a [FontAwesome](https://fontawesome.com/) account to get an icon kit.
   These icons are used by the plugin to beautify it.
   Once you get an icon kit, replace the `$fontawesome_kit` variable's value with a link to the kit.

### Activating

To install the plugin, place this directory in the `wordpress/wp-content/plugins/` directory of your local installation.
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
