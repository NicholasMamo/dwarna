<?php

/**
 * The plugin bootstrap file
 *
 * This file is read by WordPress to generate the plugin information in the plugin
 * admin area. This file also includes all of the dependencies used by the plugin,
 * registers the activation and deactivation functions, and defines a function
 * that starts the plugin.
 *
 * @link              https://github.com/NicholasMamo
 * @since             1.0.0
 * @package           Dwarna
 *
 * @wordpress-plugin
 * Plugin Name:       Dwarna
 * Plugin URI:        https://github.com/NicholasMamo/dwarna
 * Description:       A plugin to enable dynamic consent in WordPress. The plugin is derived from Dwarna: A Blockchain Solution for Dynamic Consent in Biobanking.
 * Version:           1.0.0
 * Author:            Nicholas Mamo
 * Author URI:        https://github.com/NicholasMamo
 * License:           GPL-2.0+
 * License URI:       http://www.gnu.org/licenses/gpl-2.0.txt
 * Text Domain:       dwarna
 * Domain Path:       /languages
 */

// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
	die;
}

/**
 * Currently plugin version.
 * Start at version 1.0.0 and use SemVer - https://semver.org
 * Rename this for your plugin and update it as you release new versions.
 */
define( 'PLUGIN_NAME_VERSION', '1.0.0' );

/**
 * The code that runs during plugin activation.
 * This action is documented in includes/class-biobank-activator.php
 */
function activate_biobank() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-biobank-activator.php';
	Biobank_Activator::activate();
}

/**
 * The code that runs during plugin deactivation.
 * This action is documented in includes/class-biobank-deactivator.php
 */
function deactivate_biobank() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-biobank-deactivator.php';
	Biobank_Deactivator::deactivate();
}

register_activation_hook( __FILE__, 'activate_biobank' );
register_deactivation_hook( __FILE__, 'deactivate_biobank' );

/**
 * The core plugin class that is used to define internationalization,
 * admin-specific hooks, and public-facing site hooks.
 */
require plugin_dir_path( __FILE__ ) . 'includes/class-biobank.php';

/**
 * Begins execution of the plugin.
 *
 * Since everything within the plugin is registered via hooks,
 * then kicking off the plugin from this point in the file does
 * not affect the page life cycle.
 *
 * @since    1.0.0
 */
function run_biobank() {

	$plugin = new Biobank();
	$plugin->run();

}
run_biobank();
