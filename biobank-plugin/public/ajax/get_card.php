<?php

/**
 * Get the currently logged-in user's temporary card.
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require(realpath(dirname(__FILE__)) . "/../../../../../wordpress/wp-load.php");

if (isset($_GET["temp"]))	{
	/*
	 * Create a new handler and fetch the currently logged-in participant's temporary card.
	 */
	$temp = $_GET["temp"] === "true";
	$participant_form_handler = new \client\form\ParticipantFormHandler();
	$response = $participant_form_handler->get_card($temp=$temp);
	if (empty($response->error)) { // if there are no errors, return the data
		echo $response->data;
		exit;
	}
}

echo false; // if there was an error, return false

?>
