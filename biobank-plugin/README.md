![](https://github.com/NicholasMamo/dwarna/raw/master/assets/logo.png "Dwarna Logo")

# WordPress Plugin

The WordPress plugin that handles all biobanking functionality in the frontend.

## Installing and Activating the Plugin

To install the plugin, place it in the `wordpress/wp-content/plugins/` directory of your local installation. Then, navigate to the _Installed Plugins_ tab under the _Plugins_ menu and activate the `Biobank Permissions` plugin.

Once activated, the plugin automatically generates two pages that contain the consenting procedure and the consent trail functionality.

## Deactivating and Removing the Plugin

The plugin can be deactivated or removed from the the _Installed Plugins_ tab under the _Plugins_ menu. To deactivate the plugin, press on the _Deactivate_ link under the plugin. This cleans the database from the plugin's data, and removes the automatically-generated pages. To remove the plugin directly, press on the _Remove_ link after deactivating the plugin.

## Shortcodes

The consenting procedure and the consent trail functionality can be added to any page and post using the `[biobank-consent type="all"]` and `[biobank-trail]` WordPress shortcodes.
