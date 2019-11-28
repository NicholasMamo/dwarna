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
	if (isset($_GET["error"]) && ! empty($_GET["error"])) {
		echo create_error_notice($_GET["error"]);
	} else if (isset($_GET["error"]) && isset($_GET["redirect"])) {
		echo create_success_notice("Subscriptions " . $notices[$_GET["redirect"]]);
	}
	$_GET["error"] = "";
?>

<form class="<?= $this->plugin_name ?>-form" id="recruitment-form"
	  method="post" name="recruitment_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="update_recruitment">
	<?php wp_nonce_field("recruitment_form", "recruitment_nonce"); ?>

	<div class='row my-2'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-name">Name</label>
		</div>
		<div class='col-md-5'>
			<input id='<?= $this->plugin_name ?>-name'
				   name='<?= $this->plugin_name ?>[name]'
				   type='text' ?>
		</div>
	</div>

	<div class='row my-2'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-email">Email</label>
		</div>
		<div class='col-md-5'>
			<input id='<?= $this->plugin_name ?>-email'
				   name='<?= $this->plugin_name ?>[email]'
				   type='email' ?>
		</div>
	</div>

	<div class='row my-2'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-mobile">Mobile</label>
		</div>
		<div class='col-md-5'>
			<input id='<?= $this->plugin_name ?>-mobile'
				   name='<?= $this->plugin_name ?>[mobile]'
				   type='text' ?>
		</div>
	</div>

	<div class='row my-2'>
		<div class='col-md-7 offset-md-5'>
			<input type = "submit" class = "btn btn-primary float-left" value="Become a research partner" />
		</div>
	</div>
</form>
