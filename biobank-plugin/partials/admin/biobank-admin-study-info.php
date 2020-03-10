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

/*
 * Get the page's name, and copy the session variables into the query string container.
 * Then, clear the session variables.
 */
$plugin_page = $_GET["page"];
$admin_page = "admin.php?page=$plugin_page";
$request_handler = new \client\form\StudyFormHandler(); // used to send GET requests to the backend.
$error = "";

/*
 * Fetch the study if an ID is given.
 */
$study_researchers = array();
if (isset($_GET["study_id"])) {
	$study_id = (int) $_GET["study_id"];
	$study_info = $request_handler->get_study($study_id);

	if (empty($study_info->error)) {
		$study = $study_info->study; // extract the study

		/*
		 * Extract the researchers, loading their information from WordPress.
		 */
		$study_researchers_info = $study_info->researchers;
		foreach ($study_researchers_info as $researcher) {
			$study_researchers[$researcher->user_id] = get_user_by("login", $researcher->user_id)->display_name;
		}

		if (!in_array(wp_get_current_user()->user_login, array_keys($study_researchers))) {
			$error = "You are not authorized to view that study";
			$study = new stdClass();
		} else {
			$study_participants = $request_handler->get_participants_by_study($study_id);
		}
	} else {
		$error = "Study does not exist";
		$study = new stdClass();
	}
}

/*
 * Load existing researchers to populate the fields.
 */
$existing_researchers = get_users(array(
	"role" => "researcher"
));

$researchers = array();
foreach($existing_researchers as $researcher) {
	$researchers[$researcher->user_login] = $researcher->display_name;
}

/*
 * Pagination setup
 */

$page = max(1, isset($_GET['paged']) ? $_GET['paged'] : 1); // get the current page number
$studies_per_page = 5; // the number of studies per page
$search = isset($_GET["search"]) ? $_GET["search"] : ""; // get the search string

/*
 * Fetch existing studies by searching in their names and descriptions.
 */
$existing_studies = $request_handler->search_researcher_studies(wp_get_current_user()->user_login, $studies_per_page, $page, $search);
$error = isset($existing_studies->error) && !empty($existing_studies->error) ? $existing_studies->error : $error;
$_GET["biobank_error"] = empty($_GET["biobank_error"]) ? $error : $_GET["biobank_error"];

$studies = $existing_studies->data;
$total_studies = isset($existing_studies->total) ? $existing_studies->total : 0;

$big = 999999999; // need an unlikely integer
$pagination = (paginate_links( array(
	"base" => str_replace( $big, "%#%", esc_url( get_pagenum_link( $big ) ) ),
	"format" => "?paged=%#%",
	"add_fragment" => empty($search) ? "" : "&search=$search",
	"current" => $page,
	"total" => ceil($total_studies / $studies_per_page)
)));

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <p>View biobank studies</p>

	<?php
		if (isset($_GET["biobank_error"]) && ! empty($_GET["biobank_error"])) {
		    echo create_error_notice($_GET["biobank_error"]);
		} else if (isset($_GET["biobank_error"]) && isset($_GET["redirect"])) {
		    echo create_success_notice("Study " . $notices[$_GET["redirect"]]);
		}
		$_GET["biobank_error"] = "";
	?>

    <form class="<?= $this->plugin_name ?>-form" id="study_form" method="post" name="study_form">
        <input type="hidden" name="action" value="<?= $action ?>_study">
        <?php wp_nonce_field("study_form", "study_nonce"); ?>

		<table class="form-table">
			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-study_id">ID</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
						   maxlength="60" name="<?php echo $this->plugin_name; ?>[study_id]"
						   type="text" id="<?php echo $this->plugin_name; ?>-study_id"
						   value="<?= isset($study_id) ? $study_id : "" ?>" aria-required="true" readonly >
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-name">Name</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
						   maxlength="60" name="<?php echo $this->plugin_name; ?>[name]"
						   type="text" id="<?php echo $this->plugin_name; ?>-name"
						   value="<?= isset($study->name) ? $study->name : "" ?>" aria-required="true" readonly >
				</td>
			</tr>

			<tr class="form-field form-required">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-description">Description</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
						   maxlength="60" name="<?php echo $this->plugin_name; ?>[description]"
						   type="text" id="<?php echo $this->plugin_name; ?>-description"
						   value="<?= isset($study->description) ? $study->description : "" ?>" aria-required="true" readonly >
				</td>
			</tr>

			<tr class="form-field form">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-homepage">Homepage</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
						   maxlength="60" name="<?php echo $this->plugin_name; ?>[homepage]"
						   type="text" id="<?php echo $this->plugin_name; ?>-homepage"
						   value="<?= isset($study->homepage) ? $study->homepage : "" ?>" aria-required="true" readonly >
				</td>
			</tr>

			<tr class="form-field biobank-form-decremental">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>[researchers]">Researchers</label>
				</th>
				<td>
					<?= \fields\decremental_list($study_researchers) ?>
				</td>
			</tr>

			<tr class="form-field form">
				<th scope="row">
					<label for="<?php echo $this->plugin_name; ?>-participants">Participants</label>
				</th>
				<td>
					<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
						   maxlength="60" name="<?php echo $this->plugin_name; ?>[participants]"
						   type="text" id="<?php echo $this->plugin_name; ?>-participants"
						   value="<?= isset($study_participants->data) ? count($study_participants->data) : 0 ?>" aria-required="true" readonly >
				</td>
			</tr>

		</table>

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
				<?php $study = $data->study; ?>
				<tr>
					<th scope="row"><?= $study->name ?></th>
					<td><a href="<?= $admin_page ?>&action=view&study_id=<?= $study->study_id ?>">View</a></td>
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
				<input autocapitalize="none" autocomplete="off" autocorrect="off" autofill="false"
					   maxlength="60" name="search" placeholder="Search existing studies..." type="text" value="" aria-required="true"> <?= submit_button("Search", "secondary", $this->plugin_name . "-search") ?>
			</form>
		</div>

	</div>

</div>
