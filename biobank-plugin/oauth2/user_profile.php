<?php

/**
 * Get the logged-in user's details.
 * This script does not return sensitive data beyond the username and email address.
 * The password is hashed.
 *
 * The returned data takes the following form:
 * { ID: '1',
 *		user_login: 'nicholas',
 *		user_pass: '$P$BJTBqvJ4/KAz/H9nBzIxAJA3rnKpUI1',
 *		user_nicename: 'nicholas',
 *		user_email: 'nicholas.mamo@um.edu.mt',
 *		user_url: '',
 *		user_registered: '2018-08-01 08:34:32',
 *		user_activation_key: '',
 *		user_status: '0',
 *		display_name: 'nicholas' }
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once(realpath(dirname(__FILE__)) . "/../../../../wp-load.php");

require_once __DIR__ . '/server.php';

/*
 * Verify that the access token is valid.
 */
if (!$server->verifyResourceRequest(OAuth2\Request::createFromGlobals())) {
	$server->getResponse()->send();
	die;
}

/*
 * Get the access token from the authorization header.
 * Use this unique access token to get the user for whom it was issued.
 */
$headers = apache_request_headers();
$auth = $headers["Authorization"];
$token = substr($auth, strpos($auth, " ") + 1);
$user = get_users(array('meta_key' => 'access_token', 'meta_value' => $token))[0];

/*
 * Return the basic user data.
 */
echo json_encode($user->data);

?>
