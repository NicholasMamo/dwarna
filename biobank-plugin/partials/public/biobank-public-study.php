<?php
if (isset($error) && ! empty($error)) {
?>
<div class="error">
	<?= $error ?>
</div>
<?php
} else if (isset($_GET['return']) && $_GET['return'] = 'update_consent') {
?>
<div class="<?= $this->plugin_name ?>-alert">
	Consent will be confirmed soon
</div>
<?php
}
?>

<input id='study-name' type='hidden' value='<?= $study->study->name ?>' />

<form class="<?= $this->plugin_name ?>-form" id="consent-form-<?= $study->study->study_id ?>"
	  method="post" name="consent_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="consent_form">
	<?php wp_nonce_field("consent_form", "consent_nonce"); ?>

	<p class="biobank-description"><?= $study->study->description ?></p>
	<p class="biobank-homepage"><a href="<?= $study->study->homepage ?>" target="_blank">Read more</a></p>
	<?php include_once(plugin_dir_path(__FILE__) . '/components/biobank-study-quiz.php') ?>

	<h2>Consent Update</h2>

	<label class='checkbox-container'
		   for="<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>">Participate
	   <input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>'
	   		  name = '<?= $this->plugin_name ?>[study][consent]'
			  class = 'study-consent' type = 'checkbox'>
	   <span class='checkbox'></span>
   </label>

	<input name='<?= $this->plugin_name ?>[study][study_id]'
		   type='hidden' value='<?= $study->study->study_id ?>'>
	<input id='<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-address'
		   name='<?= $this->plugin_name ?>[address]'
		   type='hidden' value=''>

	<input type = "submit" class = "btn btn-primary float-left" disabled />
</form>

<h2>Consent trail</h2>

<?php include_once(plugin_dir_path(__FILE__) . '/components/biobank-consent-trail.php') ?>
