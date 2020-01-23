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

require_once(plugin_dir_path(__FILE__) . "../ui/buttons.php");
require_once(plugin_dir_path(__FILE__) . "../ui/fields.php");
require_once(plugin_dir_path(__FILE__) . "../ui/notices.php");

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
	?>

    <form class="<?= $this->plugin_name ?>-form" id="connection_form" method="post" name="connection_form" action="options.php">
		<?php settings_fields($this->plugin_name); ?>
		<?php do_settings_sections($this->plugin_name); ?>

		<h2 class="title">REST API</h2>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-scheme">Scheme</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[scheme]"
						   type="text" id="<?php echo $this->plugin_name; ?>-scheme"
						   value="<?= $scheme ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-host">Host</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[host]"
						   type="text" id="<?php echo $this->plugin_name; ?>-host"
						   value="<?= $host ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-port">Port</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[port]"
						   type="text" id="<?php echo $this->plugin_name; ?>-port"
						   value="<?= $port ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-token-endpoint">Token endpoint</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[token-endpoint]"
						   type="text" id="<?php echo $this->plugin_name; ?>-token-endpoint"
						   value="<?= $token_endpoint ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-client-id">Client ID</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[client-id]"
						   type="text" id="<?php echo $this->plugin_name; ?>-client-id"
						   value="<?= $client_id ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-client-secret">Client secret</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[client-secret]"
						   type="text" id="<?php echo $this->plugin_name; ?>-client-secret"
						   value="<?= $client_secret ?>" aria-required="true">
				</td>
			</tr>

		</table>

        <?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
    </form>

</div>
