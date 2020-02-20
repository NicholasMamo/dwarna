<?php

/**
 * Provide an area where research partners can update their subscription preferences.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/public/partials
 */

require_once(plugin_dir_path(__FILE__) . "../ui/notices.php");

?>

<?php
	if (isset($_GET["biobank_error"]) && ! empty($_GET["biobank_error"])) {
		echo create_error_notice("Something went wrong and the email could not be sent!");
	} else if (isset($_GET["biobank_error"]) && isset($_GET["redirect"])) {
		switch ($_GET['redirect']) {
			case 'send':
				echo create_success_notice("Email sent");
				break;
		}
	}
?>

<form class="<?= $this->plugin_name ?>-form" id="recruitment-form"
	  method="post" name="recruitment_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="new_recruitment">
	<?php wp_nonce_field("recruitment_form", "recruitment_nonce"); ?>

	<label for="<?= $this->plugin_name ?>-name">Name</label>
	<input id='<?= $this->plugin_name ?>-name'
		   name='<?= $this->plugin_name ?>[name]'
		   type='text' ?>

	<label for="<?= $this->plugin_name ?>-email">Email</label>
	<input id='<?= $this->plugin_name ?>-email'
		   name='<?= $this->plugin_name ?>[email]'
		   type='email' ?>

	<label for="<?= $this->plugin_name ?>-mobile">Mobile</label>
	<input id='<?= $this->plugin_name ?>-mobile'
		   name='<?= $this->plugin_name ?>[mobile]'
		   type='text' ?>

	<input type = "submit" value="Become a research partner" />
</form>
