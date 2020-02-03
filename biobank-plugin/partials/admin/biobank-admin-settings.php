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

	<h2 class="title">REST API</h2>
    <form class="<?= $this->plugin_name ?>-form" id="rest-form" method="post" name="rest-form" action="options.php">
		<?php settings_fields("{$this->plugin_name}-rest"); ?>
		<?php do_settings_sections("{$this->plugin_name}-rest"); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-scheme">Scheme</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[scheme]"
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
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[host]"
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
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[port]"
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
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[token-endpoint]"
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
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[client-id]"
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
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-rest[client-secret]"
						   type="text" id="<?php echo $this->plugin_name; ?>-client-secret"
						   value="<?= $client_secret ?>" aria-required="true">
				</td>
			</tr>

		</table>

        <?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
    </form>

	<h2 class="title">OAuth 2.0</h2>
	<form class="<?= $this->plugin_name ?>-form" id="oauth-form" method="post" name="oauth-form" action="options.php">
		<?php settings_fields("{$this->plugin_name}-oauth"); ?>
		<?php do_settings_sections("{$this->plugin_name}-oauth"); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-proxy-from">Proxy (from)</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" name="<?php echo $this->plugin_name; ?>-oauth[proxy-from]"
						   type="text" id="<?php echo $this->plugin_name; ?>-proxy-from"
						   value="<?= $proxy_from ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-proxy-to">Proxy (to)</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" name="<?php echo $this->plugin_name; ?>-oauth[proxy-to]"
						   type="text" id="<?php echo $this->plugin_name; ?>-proxy-to"
						   value="<?= $proxy_to ?>" aria-required="true">
					<p class="description" id="proxy-description">
						The OAuth 2.0 proxy settings are used by the OAuth 2.0 system (<code>oauth/access_token.php</code> and <code>oauth/auth.php</code>).
					</p>
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-base-path">WordPress base path</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>-oauth[base-path]"
						   type="text" id="<?php echo $this->plugin_name; ?>-base-path"
						   value="<?= $base_path ?>" aria-required="true">

					<p class="description" id="base-path-description">
						The base path to the website.
						If the URL to this WordPress website is <code>example.com</code> the base path is an empty string.
						If the URL is <code>example.com/wordpress</code>, then the base path is <code>wordpress</code>.
					</p>
				</td>
			</tr>

		</table>

		<?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
	</form>

	<h2 class="title">Hyperledger Composer</h2>
	<form class="<?= $this->plugin_name ?>-form" id="composer-form" method="post" name="composer-form" action="options.php">
		<?php settings_fields("{$this->plugin_name}-composer"); ?>
		<?php do_settings_sections("{$this->plugin_name}-composer"); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-hyperledger-host">Hyperledger Composer host - WordPress</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" name="<?php echo $this->plugin_name; ?>-composer[hyperledger-host]"
						   type="text" id="<?php echo $this->plugin_name; ?>-hyperledger-host"
						   value="<?= $hyperledger_host ?>" aria-required="true">

					<p class="description" id="hyperledger-composer-host-description">
						The path where Hyperledger Composer is being hosted.
						<strong>This path should be to a WordPress blog</strong> and is used to fetch the Hyperledger Composer access token.
					</p>
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-auth-url">Hyperledger Composer authentication URL</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" name="<?php echo $this->plugin_name; ?>-composer[auth-url]"
						   type="text" id="<?php echo $this->plugin_name; ?>-auth-url"
						   value="<?= $auth_url ?>" aria-required="true">

					<p class="description" id="hyperledger-composer-authorization-url-description">
						The authorization URL for the Hyperledger Composer REST API.
					</p>
				</td>
			</tr>

		</table>

		<?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
	</form>

	<h2 class="title">Other</h2>
	<form class="<?= $this->plugin_name ?>-form" id="other-form" method="post" name="other-form" action="options.php">
		<?php settings_fields("{$this->plugin_name}-other"); ?>
		<?php do_settings_sections("{$this->plugin_name}-other"); ?>

		<table class="form-table">

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-fontawesome-kit">FontAwesome kit URL</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off"
						   autofill="false" name="<?php echo $this->plugin_name; ?>-other[fontawesome-kit]"
						   type="text" id="<?php echo $this->plugin_name; ?>-fontawesome-kit"
						   value="<?= $fontawesome_kit ?>" aria-required="true">

					<p class="description" id="fontawesome-kit-description">
						FontAwesome kits are used by the plugin to draw symbols.
						The URL looks something like <code>https://kit.fontawesome.com/xxxxxxxxxx.js</code>.
						You can obtain a kit by registering at <a href="https://fontawesome.com" target="_blank">fontawesome.com</a>.
					</p>
				</td>
			</tr>

		</table>

		<?php submit_button("Save Changes", "primary", "submit", TRUE); ?>
	</form>

</div>
