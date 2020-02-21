<?php

require_once(plugin_dir_path(__FILE__) . "../ui/fields.php");

$error = isset($defaults->error) && ! empty($defaults->error) ? $defaults->error : $error;
$refresh = (isset($_GET["return"]) && $_GET["return"] == "update_consent");

?>
<div class='biobank-consent container'>

	<form id='study-form' method="post" name="consent_form"
		  action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
		<input type="hidden" name="action" value="study_form">
		<?php wp_nonce_field("consent_form", "consent_nonce"); ?>
		<input id='<?= $this->plugin_name ?>-study'
			   name='<?= $this->plugin_name ?>[study][study_id]'
			   type='hidden' value=''>
	</form>

	<div id='<?= $this->plugin_name ?>-alerts'>
		<noscript>
			<p id='<?= $this->plugin_name ?>-no-javascript'
			   class='<?= $this->plugin_name ?>-alert'>
				You need a browser that supports JavaScript to use Dwarna!
			</p>
		</noscript>
		<p id='<?= $this->plugin_name ?>-get-temporary-card'
		   class='<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-hidden'>
			Creating a new blockchain identity
		</p>
		<p id='<?= $this->plugin_name ?>-get-credentials-card'
		   class='<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-hidden'>
			Getting existing blockchain identity
		</p>

		<p id='<?= $this->plugin_name ?>-import-card'
		   class='<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-hidden'>
			Importing blockchain identity
		</p>

		<p id='<?= $this->plugin_name ?>-save-card'
		   class='<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-hidden'>
			Saving blockchain identity
		</p>

		<p id='<?= $this->plugin_name ?>-redirect'
		   class='<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-hidden'>
			Redirecting
		</p>
	</div>

	<?php if (count($consented_studies)): ?>
		<h2>Consented Studies</h2>
		<ul>
		<?php foreach ($consented_studies as $study) { ?>
			<li><a href='#' onclick='getCard(this, "<?= $study->study_id ?>"); return false;'><?= $study->name ?></a></li>
		<?php } ?>
		</ul>
	<?php endif ?>

	<?php if (count($non_consented_studies)): ?>
		<h2>Other Studies</h2>
		<ul>
		<?php foreach ($non_consented_studies as $study) { ?>
			<li><a href='#' onclick='getCard(this, "<?= $study->study_id ?>"); return false;'><?= $study->name ?></a></li>
		<?php } ?>
		</ul>
	<?php endif ?>
</div>
