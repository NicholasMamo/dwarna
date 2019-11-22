<?php

/**
 * Provide an area where biobankers can create, edit and remove researchers
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin/partials
 */

require_once(plugin_dir_path(__FILE__) . "../ui/buttons.php");
require_once(plugin_dir_path(__FILE__) . "../ui/notices.php");

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <p>Add, edit or remove biobank researchers</p>

	<?php
		if (isset($_GET["error"]) && !empty($_GET["error"])) {
		    echo create_error_notice($_GET["error"]);
		} else if (isset($_GET["error"]) && isset($_GET["redirect"])) {
		    echo create_success_notice("Researcher " . $notices[$_GET["redirect"]]);
		}
		$_GET["error"] = "";
	?>

    <form class="<?= $this->plugin_name ?>-form" id="researcher_form" method="post" name="researcher_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
        <input type="hidden" name="action" value="<?= $action ?>_researcher">
        <?php wp_nonce_field("researcher_form", "researcher_nonce"); ?>

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

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-first_name">First Name <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[first_name]" type="text" id="<?php echo $this->plugin_name; ?>-first_name" value="<?= $action != "create" ? $user_meta["first_name"][0] : "" ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-last_name">Last Name <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[last_name]" type="text" id="<?php echo $this->plugin_name; ?>-last_name" value="<?= $action != "create" ? $user_meta["last_name"][0] : "" ?>" aria-required="true">
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
					<label for="<?php echo $this->plugin_name; ?>-affiliation">Affiliation</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[affiliation]" type="text" id="<?php echo $this->plugin_name; ?>-affiliation" value="<?= $action != "create" ? $user_meta["affiliation"][0] : "" ?>" aria-required="true">
				</td>
			</tr>

			<tr class="form-field">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-role">Role</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[role]" type="text" id="<?php echo $this->plugin_name; ?>-role" value="<?= $action != "create" ? $user_meta["role"][0] : "" ?>" aria-required="true">
				</td>
			</tr>

		</table>

        <?php submit_button($button_labels[$action] . " researcher", $button_types[$action], "submit", TRUE); ?>
    </form>

	<div class="biobank-side">
		<table class="wp-list-table widefat">
			<thead>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Researchers</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</thead>
			<tbody>
			<?php foreach ($existing_researchers as $researcher) { ?>
				<tr>
					<th scope="row"><?= $researcher->data->display_name ?></th>
					<td><a href="<?= $admin_page ?>&action=update&username=<?= $researcher->data->user_login ?>">Edit</a></td>
					<td><a href="<?= $admin_page ?>&action=remove&username=<?= $researcher->data->user_login ?>">Remove</a></td>
				</tr>
			<?php } ?>
			</tbody>
			<tfoot>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Researchers</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</tfoot>
		</table>

		<div class="biobank-footer">
			<div class="<?= $this->plugin_name ?>-float-left"><?= strlen($pagination) > 0 ? "Pages: " . $pagination : "" ?></div>
			<form class="<?= $this->plugin_name ?>-simple-form <?= $this->plugin_name ?>-float-right" id="search_form" method="get" name="search_form" action="<?= admin_url($admin_page) ?>">
				<input name="page" type="hidden" value="<?= $plugin_page ?>" />
				<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="search" placeholder="Search existing researchers..." type="text" value="" aria-required="true"> <?= submit_button("Search", "secondary", $this->plugin_name . "-search") ?>
			</form>
		</div>

	</div>

</div>
