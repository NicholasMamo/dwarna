<?php

/**
 * Authorize applications to access the user's data.
 * The script assumes and requires that the application is trusted.
 * Since the script is trusted, it only asks the user to log in and grants authorization implicitly.
 *
 * If the user is not logged in, they are asked to log in.
 * After logging in, they return to this page.
 * At this point, an authorization code is created and returned using a GET request.
 *
 * Example:
 *	- http://localhost/wordpress/wp-content/plugins/biobank/oauth2/auth.php?callback=http://localhost/wordpress/wp-content/plugins/biobank/oauth2/dump.php
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once("/var/www/html/wordpress/wp-load.php");

require_once(__DIR__.'/server.php');
require(plugin_dir_path(__FILE__) . "../includes/globals.php");

$options = get_option('biobank-oauth');

/*
 * Add a trailing slash to the base path if need be.
 */
if (strlen($options['base-path']) && substr($options['base-path'], -1) != "/") {
	$options['base-path'] = "$options['base-path']/";
}

$request = OAuth2\Request::createFromGlobals();
if ($options['proxy-from']) {
	if ($request->query('redirect_uri')) {
	        $request->query['redirect_uri'] = str_replace($options['proxy-from'], $options['proxy-to'], $request->query("redirect_uri"));
	} else {
	        $request->request["redirect_uri"] = str_replace($options['proxy-from'], $options['proxy-to'], $request->request("redirect_uri"));
	}
}

$response = new OAuth2\Response();

// Validate the authorization request.
if (!$server->validateAuthorizeRequest($request, $response)) {
	$response->send();
}

if (isset($_GET["redirect_uri"])) {
	/**
	 * The callback URL is required.
	 * The user data is returned to this URL.
	 */
	$redirect_uri = $_GET["redirect_uri"];
	$redirect_uri = str_replace($options['proxy-from'], $options['proxy-to'], $redirect_uri);
	$state = $_GET["state"];

	/*
	 * Get the currently-logged in user.
	 * If they're logged in, return the full user data.
	 * Otherwise, ask the user to log in.
	 */
	$user = wp_get_current_user();
	if ($user->ID== 0) {
		/*
		 * Redirect with instructions to return here after execution.
		 */
		$redirect = urlencode("http://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]");
		header("Location: http://$_SERVER[HTTP_HOST]/" . $options['base-path'] . "wp-login.php?redirect_to=$redirect");
		exit; // Ensure that no more code is executed from this point onwards.
	}

	/*
	 * There are no checks for whether the user authorized the application.
	 * Instead, a `true` flag is set immediately.
	 *
	 * The authorization code is extracted from the header.
	 * The code is first saved as WordPress user meta.
	 * The access token part of the flow uses this meta data to identify users.
	 * This procedure is safe because authorization codes are the primary key and therefore unique.
	 *
	 * Then, the code is sent in a GET form along with the state (for application verification).
	 */
	$server->handleAuthorizeRequest($request, $response, true);
	$code = substr($response->getHttpHeader('Location'), strpos($response->getHttpHeader('Location'), 'code=')+5, 40);
	update_user_meta( $user->ID, "authorization_code", $code );

}

?>
<html>
	<head>
		<script type="text/javascript">
			/**
			 * Submit the form immediately when the page loads.
			 */
			document.onreadystatechange = function () {
				if (document.readyState === "interactive") {
					document.getElementById("dataForm").submit();
				}
			};
		</script>
	</head>
	<body>
		<form id="dataForm" action="<?= $redirect_uri ?>" method="get" hidden>
			<input name="code" type="text" value="<?= $code ?>">
			<input name="state" type="text" value="<?= $state ?>">
		</form>
	</body>
</html>
