<?php

require_once(plugin_dir_path(__FILE__) . "ui/fields.php");
require_once(plugin_dir_path(__FILE__) . "../../client/form/consent_form_handler.php");

$error = "";
$consent_handler = new \client\form\ConsentFormHandler();

$active_studies = $consent_handler->get_active_studies();
$error = isset($active_studies->error) && ! empty($active_studies->error) ? $active_studies->error : $error;

/*
 * Extract a list of studies that are active.
 * These will later be used to separate consented studies from non-consented ones.
 */
$all_studies = array();
foreach ($active_studies->data as $study) {
	array_push($all_studies, $study->study->study_id);
}

$error = isset($defaults->error) && ! empty($defaults->error) ? $defaults->error : $error;
$refresh = (isset($_GET["return"]) && $_GET["return"] == "update_consent");

/*
 * Get the list of active studies that the user has consented to.
 * Only retain the study IDs.
 */
// $participant_studies = $consent_handler->get_studies_by_participant();
// $error = isset($participant_studies->error) && ! empty($participant_studies->error) ? $participant_studies->error : $error;
//
// $consented_studies = array();
// foreach ($participant_studies->data as $study) {
// 	array_push($consented_studies, $study->study->study_id);
// }
// $non_consented_studies = array_diff($all_studies, $consented_studies); // get the study IDs of studies that the participant has not consented to

?>
<div class='biobank-consent container'>

	<?php
	if (isset($error) && ! empty($error)) {
	?>
	<div class="error">
		<?= $error ?>
	</div>
	<?php
	} else if ($refresh) {
	?>
	<div class="error">
		Consent will be confirmed soon
	</div>
	<?php
	}
	?>

	<?php
	// foreach ($participant_studies->data as $study) {
		// $consent = true;
		// include(plugin_dir_path(__FILE__) . "components/study.php");
	// }
	?>

	<?php foreach ($active_studies->data as $study) {
		$consent = false;
		// if (in_array($study->study->study_id, $non_consented_studies)) {
		include(plugin_dir_path(__FILE__) . "components/study.php");
		// }
	} ?>
</div>
