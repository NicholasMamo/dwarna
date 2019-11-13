<?php

/**
 * Provide an area where biobankers can create, edit and remove research partners.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin/partials
 */

require(plugin_dir_path(__FILE__) . "../../includes/globals.php");
require_once(plugin_dir_path(__FILE__) . "ui/buttons.php");
require_once(plugin_dir_path(__FILE__) . "ui/notices.php");

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <p>Add, edit or remove biobank research partners</p>

	<?php
		if (isset($_GET["error"]) && !empty($_GET["error"])) {
		    echo create_error_notice($_GET["error"]);
		} else if (isset($_GET["error"]) && isset($_GET["redirect"])) {
		    echo create_success_notice("Research partner " . $notices[$_GET["redirect"]]);
		}
		$_GET["error"] = "";
	?>

    <form class="<?= $this->plugin_name ?>-form" id="participant_form" method="post" name="participant_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
        <input type="hidden" name="action" value="<?= $action ?>_participant">
        <?php wp_nonce_field("participant_form", "participant_nonce"); ?>

		<table class="form-table">
			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-username">Username <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[username]" type="text" id="<?php echo $this->plugin_name; ?>-username" value="<?= $action != "create" ? $username : "" ?>" aria-required="true" <?= $action != "create" ? "readonly" : "" ?>>
					<?= $action != "create" ? "<span class = 'description'>Usernames cannot be changed.</span>" : "" ?>
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-email">Email <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[email]" type="text" id="<?php echo $this->plugin_name; ?>-email" value="<?= $action != "create" ? $user->data->user_email : "" ?>" aria-required="true">
				</td>
			</tr>

			<tr id="password" class="user-pass1-wrap form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-password">Password <span class="description">(required)</span></label>
				</th>
				<td>
					<input class="hidden" value=" ">
					<!-- #24364 workaround -->
					<button type="button" class="button wp-generate-pw hide-if-no-js" onclick="show_password()">Generate Password</button>
					<div class="wp-pwd hide-if-js" style="display: none;">
						<span class="password-input-wrapper">
							<input type="password" name="<?php echo $this->plugin_name; ?>[password]" id="pass1" class="regular-text" value="" autocomplete="off" data-pw="<?php echo esc_attr(wp_generate_password(12, false, false)); ?>" aria-describedby="pass-strength-result" disabled="">
						</span>
						<button type="button" class="button wp-hide-pw hide-if-no-js" data-toggle="0" aria-label="Hide password">
							<span class="dashicons dashicons-hidden"></span>
							<span class="text">Hide</span>
						</button>
						<button type="button" class="button wp-cancel-pw hide-if-no-js" data-toggle="0" aria-label="Cancel password change">
							<span class="text">Cancel</span>
						</button>
						<div style="" id="pass-strength-result" aria-live="polite"></div>
					</div>
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-first_name">First Name</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[first_name]" type="text" id="<?php echo $this->plugin_name; ?>-first_name" value="<?= $action != "create" ? $user->data->first_name : "" ?>">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-last_name">Last Name</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[last_name]" type="text" id="<?php echo $this->plugin_name; ?>-last_name" value="<?= $action != "create" ? $user->data->last_name : "" ?>">
				</td>
			</tr>

		</table>

        <?php submit_button($button_labels[$action] . " research partner", $button_types[$action], "submit", TRUE); ?>
    </form>

	<div class="biobank-side">
		<table class="wp-list-table widefat">
			<thead>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Research Partners</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</thead>
			<tbody>
			<?php foreach ($existing_research_partners as $research_partner) { ?>
				<tr>
					<th scope="row"><?= $research_partner->data->display_name ?></th>
					<td><a href="<?= $admin_page ?>&action=update&username=<?= $research_partner->data->user_login ?>">Edit</a></td>
					<td><a href="<?= $admin_page ?>&action=remove&username=<?= $research_partner->data->user_login ?>">Remove</a></td>
				</tr>
			<?php } ?>
			</tbody>
			<tfoot>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Research Partners</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</tfoot>
		</table>

		<div class="biobank-footer">
			<div class="<?= $this->plugin_name ?>-float-left"><?= strlen($pagination) > 0 ? "Pages: " . $pagination : "" ?></div>
			<form class="<?= $this->plugin_name ?>-simple-form <?= $this->plugin_name ?>-float-right" id="search_form" method="get" name="search_form" action="<?= admin_url($admin_page) ?>">
				<input name="page" type="hidden" value="<?= $plugin_page ?>" />
				<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="search" placeholder="Search research partners..." type="text" value="" aria-required="true"> <?= submit_button("Search", "secondary", $this->plugin_name . "-search") ?>
			</form>
		</div>

	</div>

</div>
