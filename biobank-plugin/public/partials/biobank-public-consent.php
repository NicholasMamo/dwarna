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

	<form id='study-form' method="post" name="consent_form"
		  action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
		<input type="hidden" name="action" value="study_form">
		<?php wp_nonce_field("consent_form", "consent_nonce"); ?>
		<input id='<?= $this->plugin_name ?>-study'
			   name='<?= $this->plugin_name ?>[study][study_id]'
			   type='hidden' value=''>
	</form>

	<ul>
	<?php foreach ($active_studies->data as $study) {?>
		<li><a href='#' onclick='getCard(this, <?= $study->study->study_id ?>); return false;'><?= $study->study->name ?></a></li>
	<?php } ?>
	</ul>
</div>
