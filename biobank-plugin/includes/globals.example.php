<?php

/*
 * Set the WP-specific capabilities.
 * These capabilities are prefixed to ensure compatibility with other plugins.
 */

$biobanker_capabilities = array(
    "read", "biobank_view_admin_menu",
    "biobank_create_participant", "biobank_edit_participant", "biobank_view_participant", "biobank_remove_participant",
	"biobank_create_researcher", "biobank_edit_researcher", "biobank_remove_researcher",
	"biobank_create_study", "biobank_edit_study", "biobank_remove_study",
	"biobank_send_email", "biobank_remove_email",
	"biobank_settings",
	"biobank_update_consent", "biobank_view_consent",
);

$researcher_capabilities = array(
    "read", "biobank_view_admin_menu",
	"biobank_view_study",
);

$participant_capabilities = array(
    "biobank_view_profile",
	"biobank_update_consent", "biobank_view_consent",
);

/*
 * Set the scopes for different user roles.
 * These scopes must be in agreement with the REST API's scopes.
 */

$scopes = array(
	"administrator" => array(
		"create_participant", "update_participant", "view_participant", "remove_participant",
		"create_researcher", "remove_researcher",
		"create_study", "update_study", "remove_study", "view_study",
		"view_consent",
		"view_email", "create_email", "remove_email",
		"view_subscription",
		"admin",
	),
	"biobanker" => array(
		"create_participant", "update_participant", "view_participant", "remove_participant",
		"create_researcher", "remove_researcher",
		"create_study", "update_study", "remove_study", "view_study",
		"view_consent",
		"view_email", "create_email", "remove_email",
		"admin",
	),
	"researcher" => array(
		"view_study", "view_consent",
	),
	"participant" => array(
		"view_study",
		"update_consent", "view_consent",
		"change_card",
		"view_subscription", "update_subscription"
	),
);

/*
 * Page information and menu visibility.
 * These pages are created by the plugin upon activated, and removed when de-activated.
 * By default, pages are visible by everyone in the menu.
 * These permissions are used by the `wp_get_nav_menu_items` filter to hide pages in the menu.
 */
$plugin_pages = array(
	"biobank-consent" => array(
		"wp_info" => array(
			"post_title" => "Ongoing Studies",
			"post_content" => "<!-- wp:shortcode -->[biobank-consent type=\"all\"]<!-- /wp:shortcode -->",
			"post_name" => "biobank-consent",
			"post_status" => "publish",
			"post_author" => 1,
			"post_type" => "page",
		),
		"menu_visibility" => array(
			"participant", "administrator",
		),
		"public" => false,
	),
	"biobank-study" => array(
		"wp_info" => array(
			"post_title" => "Study",
			"post_content" => "<!-- wp:shortcode -->[biobank-study]<!-- /wp:shortcode -->",
			"post_name" => "biobank-study",
			"post_status" => "publish",
			"post_author" => 1,
			"post_type" => "page",
		),
		"menu_visibility" => array( ),
		"public" => false,
	),
	"biobank-subscription" => array(
		"wp_info" => array(
			"post_title" => "Subscriptions",
			"post_content" => "<!-- wp:shortcode -->[biobank-subscription]<!-- /wp:shortcode -->",
			"post_name" => "biobank-subscription",
			"post_status" => "publish",
			"post_author" => 1,
			"post_type" => "page",
		),
		"menu_visibility" => array( ),
		"public" => false,
	),
	"biobank-recruitment" => array(
		"wp_info" => array(
			"post_title" => "Become a Research Partner",
			"post_content" => "<!-- wp:shortcode -->[biobank-recruitment]<!-- /wp:shortcode -->",
			"post_name" => "biobank-recruitment",
			"post_status" => "publish",
			"post_author" => 1,
			"post_type" => "page",
		),
		"menu_visibility" => array( ),
		"public" => true,
	),
);

/*
 * The client identifiers.
 */

$client_id = "abc";
$client_secret = "xyz";

/*
 * The name of the blockchain solution's access token.
 * It is assumed to be stored in a cookie.
 */
$blockchain_access_token = "access_token";

/**
 * The cookie redirect URL.
 * This URL is used to fetch the access token cookie.
 */
$hyperledger_host = "http://localhost/wordpress/wp-content/plugins/biobank-plugin/public/ajax/get_cookie.php";

/**
 * The host where the WordPress website is being served.
 */
$host = "http://localhost";

/**
 * The authorization URL for the Hyperledger Composer REST API.
 */
$auth_url = "http://localhost:3000/auth/local-wordpress";

/*
 * The key used to encrypt email addresses.
 * The key can be generated using `php -r "echo bin2hex(sodium_crypto_secretbox_keygen());" > itop_secret_key.txt`.
 */
$encryptionKey = hex2bin("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");

/*
 * The FontAwesome kit to use.
 * A kit can be downloaded from FontAwesome after registering: https://fontawesome.com/
 */
$fontawesome_kit = "https://kit.fontawesome.com/xxxxxxxxxx.js";

/*
 * OAuth 2.0 configuration.
 */
$oauth_database = "wordpress";
$oauth_host = "localhost";
$oauth_username = "root";
$oauth_password = "root";

/*
 * OAuth 2.0 proxy settings.
 * This is used by the OAuth 2.0 system (`oauth/access_token.php` and `oauth/auth.php`).
 */
$proxy_from = "";
$proxy_to = "";

/*
 * The base path to the website.
 * For example, if the URL to this WordPress website is example.com the base path is an empty string.
 * If the URL is example.com/wordpress, then the basepath is "wordpress".
 */
$base_path = "";

/**
 * SMTP settings
 */
if (!defined('SMTP_HOST')) define('SMTP_HOST', 'smtp.gmail.com'); // The hostname of the mail server
if (!defined('SMTP_PORT')) define('SMTP_PORT', '587'); // SMTP port number - likely to be 25, 465 or 587
if (!defined('SMTP_SECURE')) define('SMTP_SECURE', 'tls'); // Encryption system to use - ssl or tls
if (!defined('SMTP_AUTH')) define('SMTP_AUTH', true); // Use SMTP authentication (true|false)
if (!defined('SMTP_USER')) define('SMTP_USER', 'xyz@gmail.com'); // Username to use for SMTP authentication
if (!defined('SMTP_PASS')) define('SMTP_PASS', 'xxxxxxxxxxxxxxxx'); // Password to use for SMTP authentication
if (!defined('SMTP_FROM')) define('SMTP_FROM', 'xyz@gmail.com'); // SMTP From email address
if (!defined('SMTP_NAME')) define('SMTP_NAME', 'Dwarna'); // SMTP From name
if (!defined('SMTP_DEBUG')) define('SMTP_DEBUG', 0); // for debugging purposes only set to 1 or 2

/**
 * An option to disable administrator notifications whenever a user resets their password.
 */
if (!defined('RESET_PASSWORD_NOTIFICATION')) define('RESET_PASSWORD_NOTIFICATION', false);

?>
