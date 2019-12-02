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
require_once(plugin_dir_path(__FILE__) . "../ui/fields.php");
require_once(plugin_dir_path(__FILE__) . "../ui/notices.php");

require_once(plugin_dir_path(__FILE__) . "../../client/form/study_form_handler.php");
require_once(plugin_dir_path(__FILE__) . "../../client/request.php");

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <p>Add, edit or remove biobank studies</p>

	<?php
		if (isset($_GET["biobank_error"]) && ! empty($_GET["biobank_error"])) {
		    echo create_error_notice($_GET["biobank_error"]);
		} else if (isset($_GET["biobank_error"]) && isset($_GET["redirect"])) {
		    echo create_success_notice("Study " . $notices[$_GET["redirect"]]);
		}
		$_GET["biobank_error"] = "";
	?>

    <form class="<?= $this->plugin_name ?>-form" id="study_form" method="post" name="study_form" onsubmit="convert_values()" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
        <input type="hidden" name="action" value="<?= $action ?>_study">
        <?php wp_nonce_field("study_form", "study_nonce"); ?>

		<table class="form-table">
			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-study_id">ID <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[study_id]" type="text" id="<?php echo $this->plugin_name; ?>-study_id" value="<?= $action != "create" ? $study_id : "" ?>" aria-required="true" <?= $action != "create" ? "readonly" : "" ?>>
					<?= $action != "create" ? "<span class = 'description'>Study IDs cannot be changed.</span>" : "" ?>
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-name">Name <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[name]" type="text" id="<?php echo $this->plugin_name; ?>-name" value="<?= $action != "create" ? $study->name : "" ?>" aria-required="true" >
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-description">Description <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[description]" type="text" id="<?php echo $this->plugin_name; ?>-description" value="<?= $action != "create" ? $study->description : "" ?>" aria-required="true" >
				</td>
			</tr>

			<tr class="form-field form">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-homepage">Homepage <span class="description">(required)</span></label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="<?php echo $this->plugin_name; ?>[homepage]" type="text" id="<?php echo $this->plugin_name; ?>-homepage" value="<?= $action != "create" ? $study->homepage : "" ?>" aria-required="true" >
				</td>
			</tr>

			<tr class="form-field biobank-form-decremental">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>[researchers]">Researchers</label>
				</th>
				<td>
					<?= \fields\decremental_select($this->plugin_name . "[researchers]", $researchers, $action != "create" ? $study_researchers : array()); ?>
				</td>
			</tr>

		</table>

        <?php submit_button($button_labels[$action] . " study", $button_types[$action], "submit", TRUE); ?>
    </form>

	<div class="biobank-side">
		<table class="wp-list-table widefat">
			<thead>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Studies</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</thead>
			<tbody>
			<?php foreach ($studies as $data) { ?>
				<?php $existing_study = $data->study; ?>
				<tr>
					<th scope="row"><?= $existing_study->name ?></th>
					<td><a href="<?= $admin_page ?>&action=update&study_id=<?= $existing_study->study_id ?>">Edit</a></td>
					<td><a href="<?= $admin_page ?>&action=remove&study_id=<?= $existing_study->study_id ?>">Remove</a></td>
				</tr>
			<?php } ?>
			</tbody>
			<tfoot>
				<th scope="col" id="name" class="manage-column column-name column-primary">Existing Studies</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</tfoot>
		</table>

		<div class="biobank-footer">
			<div class="<?= $this->plugin_name ?>-float-left"><?= strlen($pagination) > 0 ? "Pages: " . $pagination : "" ?></div>
			<form class="<?= $this->plugin_name ?>-simple-form <?= $this->plugin_name ?>-float-right" id="search_form" method="get" name="search_form" action="<?= admin_url($admin_page) ?>">
				<input name="page" type="hidden" value="<?= $plugin_page ?>" />
				<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false" maxlength="60" name="search" placeholder="Search existing studies..." type="text" value="" aria-required="true"> <?= submit_button("Search", "secondary", $this->plugin_name . "-search") ?>
			</form>
		</div>

		<?php if (isset($study)): ?>
		<table class="wp-list-table widefat">
			<thead>
				<th scope="col" id="name" class="manage-column column-name column-primary">Participating Research Partners</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</thead>
			<tbody>
			<?php foreach ($research_partners as $research_partner) { ?>
				<tr>
					<th scope="row"><?= $research_partner->user_id ?></th>
					<td><a href="admin.php?page=biobank_partners&action=update&username=<?= $research_partner->user_id ?>">Edit</a></td>
					<td><a href="admin.php?page=biobank_partners&action=remove&username=<?= $research_partner->user_id ?>">Remove</a></td>
				</tr>
			<?php } ?>
			</tbody>
			<tfoot>
				<th scope="col" id="name" class="manage-column column-name column-primary">Participating Research Partners</th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
				<th scope="col" id="name" class="manage-column column-name column-primary"></th>
			</tfoot>
		</table>

		<div class="biobank-footer">
			<div class="<?= $this->plugin_name ?>-float-left"><?= strlen($pagination) > 0 ? "Pages: " . $pagination : "" ?></div>
		</div>

	<?php endif; ?>
	</div>

</div>
