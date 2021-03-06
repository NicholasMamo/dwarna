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
	"biobank_remove_participant",
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
		"remove_participant",
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
		"public" => true,
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
		"menu_visibility" => array( 'participant' ),
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
	"biobank-erasure" => array(
		"wp_info" => array(
			"post_title" => "Erase My Data",
			"post_content" => "<!-- wp:shortcode -->[biobank-erasure]<!-- /wp:shortcode -->",
			"post_name" => "biobank-erasure",
			"post_status" => "publish",
			"post_author" => 1,
			"post_type" => "page",
		),
		"menu_visibility" => array( 'participant' ),
		"public" => false,
	),
);

/**
 * The default REST API settings.
 */
$default_rest_settings = array(
	"scheme" => "http",
	"host" => "localhost",
	"port" => "7225",
	"token-endpoint" => "token",
	"client-id" => "",
	"client-secret" => "",
);

/**
 * The default Hyperledger Composer settings.
 */
$default_composer_settings = array(
	"hyperledger-host" => "http://localhost/wordpress/wp-content/plugins/biobank-plugin/public/ajax/get_cookie.php",
	"auth-url" => "http://localhost:3000/auth/local-wordpress",
);

/**
 * Other default settings.
 */
$default_settings = array(
	"login" => "wp-login.php",
);

/*
 * The name of the blockchain solution's access token.
 * It is assumed to be stored in a cookie.
 */
if (!defined('BLOCKCHAIN_ACCESS_TOKEN')) define('BLOCKCHAIN_ACCESS_TOKEN', "access_token");

/*
 * The key used to encrypt email addresses.
 * The key can be generated using `php -r "echo bin2hex(sodium_crypto_secretbox_keygen());" > itop_secret_key.txt`.
 */
if (!defined('ENCRYPTION_KEY')) define('ENCRYPTION_KEY', hex2bin("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"));

/*
 * OAuth 2.0 configuration.
 */
if (!defined('OAUTH_DATABASE')) define('OAUTH_DATABASE', 'wordpress');
if (!defined('OAUTH_HOST')) define('OAUTH_HOST', 'localhost');
if (!defined('OAUTH_USERNAME')) define('OAUTH_USERNAME', 'root');
if (!defined('OAUTH_PASSWORD')) define('OAUTH_PASSWORD', 'root');

/**
 * SMTP settings
 */
if (!defined('SMTP_HOST')) define('SMTP_HOST', 'smtp.gmail.com'); // The hostname of the mail server
if (!defined('SMTP_PORT')) define('SMTP_PORT', '587'); // SMTP port number - likely to be 25, 465 or 587
if (!defined('SMTP_SECURE')) define('SMTP_SECURE', 'tls'); // Encryption system to use—ssl or tls—or empty for no encryption
if (!defined('SMTP_AUTH')) define('SMTP_AUTH', true); // Use SMTP authentication (true|false)
if (!defined('SMTP_USER')) define('SMTP_USER', 'xyz@gmail.com'); // Username to use for SMTP authentication
if (!defined('SMTP_PASS')) define('SMTP_PASS', 'xxxxxxxxxxxxxxxx'); // Password to use for SMTP authentication
if (!defined('SMTP_FROM')) define('SMTP_FROM', 'xyz@gmail.com'); // SMTP From email address
if (!defined('SMTP_NAME')) define('SMTP_NAME', 'Dwarna'); // SMTP From name
if (!defined('SMTP_DEBUG')) define('SMTP_DEBUG', 0); // for debugging purposes only set to 1 or 2
if (!defined('SMTP_AUTOTLS')) define('SMTP_AUTOTLS', true); // Enable TLS by default (true|false)

/**
 * An option to disable administrator notifications whenever a user resets their password.
 */
if (!defined('RESET_PASSWORD_NOTIFICATION')) define('RESET_PASSWORD_NOTIFICATION', false);

?>
