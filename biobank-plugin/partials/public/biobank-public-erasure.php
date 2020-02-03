<?php

/**
 * Provide an area where research partners can ask that their data is erased from the biobank.
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
		echo create_error_notice($_GET["biobank_error"]);
	}
	$_GET["biobank_error"] = "";
?>

<form class="<?= $this->plugin_name ?>-form" id="erasure-form"
	  method="post" name="erasure_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="erasure">
	<?php wp_nonce_field("erasure_form", "erasure_nonce"); ?>

	<input type = "submit" class = "btn btn-primary float-left" value="I want to erase my data" />
</form>
