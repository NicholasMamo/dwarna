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

require_once(plugin_dir_path(__FILE__) . "../../client/request.php");
require_once(plugin_dir_path(__FILE__) . "../../client/form/form_handler.php");

/*
 * Get the page's name, and copy the session variables into the query string container.
 */
$plugin_page = $_GET["page"];
$admin_page = "admin.php?page=$plugin_page";
$request_handler = new \client\form\GeneralFormHandler(); // used to send GET requests to the backend.
if (!$request_handler->ping()) {
	$error = "Server could not be reached.";
}

/*
 * Load the options.
 */
$options = get_option($this->plugin_name);
$scheme = isset($options["biobank-scheme"]) ? $options["biobank-scheme"] : "http";
$host = isset($options["biobank-host"]) ? $options["biobank-host"] : "localhost";
$port = isset($options["biobank-port"]) ? $options["biobank-port"] : "8080";

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

	<h2 class="title">Server configuration</h2>

    <form class="<?= $this->plugin_name ?>-form" id="connection_form" method="post" name="connection_form" action="options.php">
		<?php settings_fields($this->plugin_name); ?>
		<?php do_settings_sections($this->plugin_name); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-scheme">Scheme</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[scheme]" type="text" id="<?php echo $this->plugin_name; ?>-scheme" value="<?= $scheme ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-host">Host</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[host]" type="text" id="<?php echo $this->plugin_name; ?>-host" value="<?= $host ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-port">Port</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[port]" type="text" id="<?php echo $this->plugin_name; ?>-port" value="<?= $port ?>" aria-required="true">
				</td>
			</tr>

		</table>

        <?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
    </form>

</div>
