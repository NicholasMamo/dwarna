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

    <form class="<?= $this->plugin_name ?>-form" id="email_form" method="post" name="email_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
		<input type="hidden" name="action" value="create_email">

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label>Recipient Group</label>
				</th>
				<td>
					<div class='radio-input-group'>
						<input name="<?= $this->plugin_name; ?>[recipient-group]"
							   type="radio" id="recipient-group-none" aria-required="true">
						<label for="recipient-group-none">No one</label>
					</div>

					<div class='radio-input-group'>
						<input name="<?= $this->plugin_name; ?>[recipient-group]"
							   type="radio" id="recipient-group-all" aria-required="true">
						<label for="recipient-group-all">All research partners</label>
					</div>
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?= $this->plugin_name; ?>-recipient">Recipient</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?= $this->plugin_name; ?>[recipient]"
						   type="text" id="<?= $this->plugin_name; ?>-recipient" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row"></th>
				<td id='recipients'>
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?= $this->plugin_name; ?>-subject">Subject</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?= $this->plugin_name; ?>[subject]"
						   type="text" id="<?= $this->plugin_name; ?>-subject" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?= $this->plugin_name; ?>-body">Body</label>
				</th>
				<td>
				<?php
					$settings = array(
						'textarea_rows' => 5,
						'media_buttons' => true
					);
					wp_editor( '', "{$this->plugin_name}-body", $settings);
				?>
				</td>
			</tr>

		</table>

        <?php submit_button("Send Email", "primary", "submit", TRUE); ?>
    </form>

</div>
