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

	<?php foreach ($active_studies->data as $study) {
		include(plugin_dir_path(__FILE__) . "components/study.php");
	} ?>
</div>
