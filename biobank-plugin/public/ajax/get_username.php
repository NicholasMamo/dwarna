<?php

/**
 * Get the currently logged-in user's name.
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once("/var/www/html/wordpress/wp-load.php");

echo wp_get_current_user()->user_login;

?>
