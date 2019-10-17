<?php

/**
 * Provide an area where biobankers can edit the plugin's settings.
 * These include the configuration that is necessary to connect with the server.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin/partials
 */

require_once(plugin_dir_path(__FILE__) . "ui/buttons.php");
require_once(plugin_dir_path(__FILE__) . "ui/fields.php");
require_once(plugin_dir_path(__FILE__) . "ui/notices.php");

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

	<?php
		if (isset($_GET["settings-updated"])) {
			echo create_success_notice("Settings saved.");
		}
		if (isset($error) && ! empty($error)) {
		    echo create_error_notice($error);
		}
		$_GET["error"] = "";
	?>

	<h2 class="title">Email</h2>

    <form class="<?= $this->plugin_name ?>-form" id="email_form" method="post" name="email_form" action="options.php">
		<?php settings_fields($this->plugin_name); ?>
		<?php do_settings_sections($this->plugin_name); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-recipient">Recipient</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[recipient]"
						   type="text" id="recipient" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row"></th>
				<td id='recipients'>
				</td>
			</tr>

		</table>

        <?php submit_button("Send Email", "primary", "submit", TRUE); ?>
    </form>

</div>
