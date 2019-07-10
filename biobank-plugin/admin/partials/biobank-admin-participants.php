<?php

/**
 * Provide an area where biobankers can create, edit and remove participants
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

/*
 * Get the page's name, and copy the session variables into the query string container.
 * Then, clear the session variables.
 */
$plugin_page = $_GET["page"];
$admin_page = "admin.php?page=$plugin_page";

/*
 * Get the kind of action that is to be performed in this form, if it is explicitly-stated.
 */
$action = isset($_GET["action"]) ? $_GET["action"] : "create";

/*
 * Fetch the user if a username is given.
 */
$username = isset($_GET["username"]) ? $_GET["username"] : "";
$user = get_user_by("login", $username);
if ($user) {
	/*
	 * If a user was provided, decrypt their email address.
	 */

	$decoded = base64_decode($user->user_email);
	$cipherNonce = mb_substr($decoded, 0, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, '8bit');
	$cipherText = mb_substr($decoded, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, null, '8bit');
	$email = sodium_crypto_secretbox_open($cipherText, $cipherNonce, $encryptionKey);
	$user->user_email = $email;
}

$action = $user ? $action : "create";

/*
 * Pagination setup
 */

$page = max(1, isset($_GET["paged"]) ? $_GET["paged"] : 1); // get the current page number
$users_per_page = 6; // the number of users per page
$search = isset($_GET["search"]) ? $_GET["search"] : ""; // get the search string

/*
 * Fetch existing participants by searching in their usernames.
 */
$existing_participants = get_users(array(
	"role" => "participant",
	"number" => $users_per_page,
	"paged" => $page,
	"search" => "*$search*",
	"search_columns" => array("user_login")
));

/*
 * Count the number of users that fit the search string.
 * This information is used to create a pagination.
 */
$query = new WP_User_Query(array(
	"role" => "participant",
	"search" => "*$search*",
	"search_columns" => array("user_login"),
));
$total_users = $query->get_total(); // the total number of users

$big = 999999999; // need an unlikely integer
$pagination = (paginate_links(array(
	"base" => str_replace($big, "%#%", get_pagenum_link($big, false)),
	"format" => "?paged=%#%",
	"add_fragment" => empty($search) ? "" : "&search=$search",
	"current" => $page,
	"total" => ceil($total_users / $users_per_page)
)));

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <p>Add, edit or remove biobank participants</p>

	<?php
		if (isset($_GET["error"]) && !empty($_GET["error"])) {
		    echo create_error_notice($_GET["error"]);
		} else if (isset($_GET["error"]) && isset($_GET["redirect"])) {
		    echo create_success_notice("Participant " . $notices[$_GET["redirect"]]);
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
		</table>

        <?php submit_button($button_labels[$action] . " participant", $button_types[$action], "submit", TRUE); ?>
    </form>

	<div class="biobank-side">
		<table class="wp-list-table widefat">
			<thead>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Participants</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</thead>
			<tbody>
			<?php foreach ($existing_participants as $participant) { ?>
				<tr>
					<th scope="row"><?= $participant->data->display_name ?></th>
					<td><a href="<?= $admin_page ?>&action=update&username=<?= $participant->data->user_login ?>">Edit</a></td>
					<td><a href="<?= $admin_page ?>&action=remove&username=<?= $participant->data->user_login ?>">Remove</a></td>
				</tr>
			<?php } ?>
			</tbody>
			<tfoot>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Participants</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</tfoot>
		</table>

		<div class="biobank-footer">
			<div class="<?= $this->plugin_name ?>-float-left"><?= strlen($pagination) > 0 ? "Pages: " . $pagination : "" ?></div>
			<form class="<?= $this->plugin_name ?>-simple-form <?= $this->plugin_name ?>-float-right" id="search_form" method="get" name="search_form" action="<?= admin_url($admin_page) ?>">
				<input name="page" type="hidden" value="<?= $plugin_page ?>" />
				<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="search" placeholder="Search existing participants..." type="text" value="" aria-required="true"> <?= submit_button("Search", "secondary", $this->plugin_name . "-search") ?>
			</form>
		</div>

	</div>

</div>
