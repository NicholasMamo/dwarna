/**
 * The Hyperledger Composer configuration.
 */

/**
 * The Hyperledger Composer API key name.
 */
const hyperledger_access_token = "access_token";

/**
 * The port where the Python REST API is listening.
 */
const biobank_backend_port = 7225;

/**
 * The website host.
 */
const host = `${window.location.protocol}//${window.location.hostname}`;

/**
 * The base path where the AJAX scripts reside.
 */
const ajax_base_path = `${host}/wordpress/wp-content/plugins/biobank-plugin/public/ajax/`;

/**
 * The blockchain host.
 */
const hyperledger_host = `${window.location.protocol}//${window.location.hostname}:3000`;

/**
 * The biobank plugin name, used in element IDs.
 */
const plugin_name = 'biobank';
