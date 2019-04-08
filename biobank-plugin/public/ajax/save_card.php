<?php

/**
 * Get the currently logged-in user's temporary card.
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once("/var/www/html/wordpress/wp-load.php");

if (isset($_FILES["card"]))	{
	/*
	 * Create a new handler and save the currently logged-in participant's credentials-ready card.
	 */
	$card = $_FILES["card"];
	ob_start();
	$length = readfile($card["tmp_name"]);
	$card_contents = ob_get_clean();;

	$participant_form_handler = new \client\form\ParticipantFormHandler();

	$response = $participant_form_handler->save_card($card=$card_contents);
	if (empty($response->error)) { // if there are no errors, return the data
		echo $response->data;
		exit;
	}
}

echo false; // if there was an error, return false

?>
