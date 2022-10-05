<?php

/**
 * Check whether the currently logged-in user has a temporary card.
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once("/var/www/html/wordpress/wp-load.php");

if (isset($_GET['study_id']))	{
	$study_id = $_GET['study_id'];
	$participant_form_handler = new \client\form\ParticipantFormHandler();
	$response = $participant_form_handler->has_consent($study_id=$study_id);
	if (empty($response->error)) { // if there are no errors, return the data
		echo $response->data;
		exit;
	}
}

echo false; // if there was an error, return false

?>
