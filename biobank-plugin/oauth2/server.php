<?php

/**
 * Initialize the server.
 */

require(plugin_dir_path(__FILE__) . "../includes/globals.php");

$dsn      = "mysql:dbname=$oauth_database;host=$oauth_host";
$username = $oauth_username;
$password = $oauth_password;

// Switch on error reporting.
ini_set('display_errors',1);
error_reporting(E_ALL);

// Auto-load the OAuth server.
require_once('OAuth2/Autoloader.php');
OAuth2\Autoloader::register();

// $dsn is the Data Source Name of the database, for exmaple `mysql:dbname=my_oauth2_db;host=localhost`.
$storage = new OAuth2\Storage\Pdo(array('dsn' => $dsn, 'username' => $username, 'password' => $password));

// Pass a storage object or array of storage objects to the OAuth2 server class.
$server = new OAuth2\Server($storage);

// Add the "Authorization Code" grant type (this is where the oauth magic happens).
$server->addGrantType(new OAuth2\GrantType\AuthorizationCode($storage));


?>
