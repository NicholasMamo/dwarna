<?php

/**
 * Trade the authorization code for an access token.
 *
 * Example:
 *	- http://localhost/wordpress/wp-content/plugins/biobank/auth.php?callback=http://localhost/wordpress/wp-content/plugins/biobank/dump.php
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once("/var/www/html/wordpress/wp-load.php");

require_once(__DIR__.'/server.php');

/*
 * Craft a response from the request.
 * The response contains the access token as a parameter.
 */
$response = $server->handleTokenRequest(OAuth2\Request::createFromGlobals());

/*
 * Get the requesting user using the supplied authorization code.
 * This procedure is safe because authorization codes are the primary key in the table and therefore unique.
 *
 * Then, extract the access token from the response parameters and save it similarly to the authorization code.
 * Again, this is safe because the access token is the primary key and therefore unique.
 * Note that this is not a security flaw - the access token should be secure all the same.
 */
$user = get_users(array('meta_key' => 'authorization_code', 'meta_value' => $_POST["code"]))[0];
$access_token = $response->getParameters()["access_token"];
update_user_meta( $user->ID, "access_token", $access_token );

$response->send();

?>
