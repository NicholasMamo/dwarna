<?php

/**
 * The admin-specific functionality of the plugin.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin
 */

 require_once(plugin_dir_path(__FILE__) . "../client/form/email_form_handler.php");
require_once(plugin_dir_path(__FILE__) . "../client/request.php");

/**
 * The admin-specific functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the admin-specific stylesheet and JavaScript.
 *
 * @package    Biobank
 * @subpackage Biobank/admin
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class Biobank_Admin {

	/**
	 * The ID of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $plugin_name    The ID of this plugin.
	 */
	private $plugin_name;

	/**
	 * The version of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $version    The current version of this plugin.
	 */
	private $version;

	/**
	 * The maximum number of items to show in every pagination page.
	 *
	 * @since	1.0.0
	 * @access	private
	 * @var		int		ITEMS_PER_PAGE	The maximum number of items to show in every paginatio page.
	 */
	private const ITEMS_PER_PAGE = 10;

	/**
	 * Initialize the class and set its properties.
	 *
	 * @since    1.0.0
	 * @param      string    $plugin_name       The name of this plugin.
	 * @param      string    $version   		The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

		/*
		 * The page slugs.
		 */
		$this->menu_pages = array(
			"top_level" => "biobank_main",
			"partners" => "biobank_partners",
			"researchers" => "biobank_researchers",
			"studies" => "biobank_studies",
			"settings" => "biobank_settings",
			"emails" => "biobank_emails",
			"view_studies" => "biobank_view_studies",
		);

	}

	/**
	 * Add the biobank top-level menu to the side menu.
	 *
	 * @since	1.0.0
	 */
	public function add_plugin_admin_menu() {
		$top_level_slug = $this->menu_pages["top_level"];

		/*
		 * Add the top-level menu
		 */
		add_menu_page(
			"Biobank Management",
			"Biobank",
			"biobank_view_admin_menu",
			$top_level_slug,
			null,
			null
		);

		/*
		 * Add all the sub-menus
		 */

		add_submenu_page(
			$top_level_slug,
			"Manage Research Partners",
			"Research Partners",
			"biobank_create_participant",
			$this->menu_pages["partners"],
			array($this, "display_research_partners_page")
		);

		add_submenu_page(
			$top_level_slug,
			"Manage Researchers",
			"Researchers",
			"biobank_create_researcher",
			$this->menu_pages["researchers"],
			array($this, "display_researchers_page")
		);

		add_submenu_page(
			$top_level_slug,
			"Manage Studies",
			"Studies",
			"biobank_create_study",
			$this->menu_pages["studies"],
			array($this, "display_studies_page")
		);

		add_submenu_page(
			$top_level_slug,
			"View Studies",
			"View Studies",
			"biobank_view_study",
			$this->menu_pages["view_studies"],
			array($this, "display_view_studies_page")
		);

		add_submenu_page(
			$top_level_slug,
			"Send Email",
			"Emails",
			"biobank_send_email",
			$this->menu_pages["emails"],
			array($this, "display_emails_page")
		);

		add_submenu_page(
			$top_level_slug,
			"Settings",
			"Settings",
			"biobank_settings",
			$this->menu_pages["settings"],
			array($this, "display_settings_page")
		);

	   remove_submenu_page($top_level_slug, $top_level_slug); // remove the default top-level sub-menu created by WordPress
	}

	/**
	 * Display the research partner management page.
	 *
	 * @since	1.0.0
	 */
	public function display_research_partners_page() {
		/*
		 * Fetch existing research partners by searching in their usernames.
		 */
		$search = isset($_GET["search"]) ? $_GET["search"] : "";
		$existing_research_partners = get_users(array(
			"role" => "participant",
			"number" => Biobank_Admin::ITEMS_PER_PAGE,
			"paged" => max(1, isset($_GET['paged']) ? $_GET['paged'] : 1),
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
		$pagination = $this->setup_pagination($total_users);

		/*
		 * Get the kind of action that is to be performed in this form, if it is explicitly-stated.
		 * Also fetch other information about the page.
		 */
		$action = isset($_GET["action"]) ? $_GET["action"] : "create";
		$plugin_page = $_GET["page"];
		$admin_page = "admin.php?page=$plugin_page";

		/*
		 * Fetch the user being edited or removed if a username is given.
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

		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-research-partners.php");
	}

	/**
	 * Display the researcher management page.
	 *
	 * @since	1.0.0
	 */
	public function display_researchers_page() {
		/*
		 * Fetch existing researchers by searching in their usernames.
		 */
		$search = isset($_GET["search"]) ? $_GET["search"] : "";
		$existing_researchers = get_users(array(
			"role" => "researcher",
			"number" => Biobank_Admin::ITEMS_PER_PAGE,
			"paged" => max(1, isset($_GET['paged']) ? $_GET['paged'] : 1),
			"search" => "*$search*",
			"search_columns" => array("user_login")
		));

		/*
		 * Count the number of users that fit the search string.
		 * This information is used to create a pagination.
		 */
		$query = new WP_User_Query(array(
			"role" => "researcher",
			"search" => "*$search*",
			"search_columns" => array("user_login"),
		));
		$total_users = $query->get_total(); // the total number of users
		$pagination = $this->setup_pagination($total_users);

		/*
		 * Get the kind of action that is to be performed in this form, if it is explicitly-stated.
		 * Also fetch other information about the page.
		 */
		$action = isset($_GET["action"]) ? $_GET["action"] : "create";
		$plugin_page = $_GET["page"];
		$admin_page = "admin.php?page=$plugin_page";

		/*
		 * Fetch the user if a username is given.
		 */
		$username = isset($_GET["username"]) ? $_GET["username"] : "";
		$user = get_user_by("login", $username);
		$user_meta = $user ? get_user_meta($user->data->ID) : array();
		$action = $user ? $action : "create";

		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-researchers.php");
	}

	/**
	 * Display the study management page.
	 *
	 * @since	1.0.0
	 */
	public function display_studies_page() {
		/*
		 * Get the kind of action that is to be performed in this form, if it is explicitly-stated.
		 */
		$action = isset($_GET["action"]) ? $_GET["action"] : "create";

		/*
		 * Fetch existing studies by searching in their names and descriptions.
		 */
		$search = isset($_GET["search"]) ? $_GET["search"] : ""; // get the search string
		$request_handler = new \client\form\StudyFormHandler(); // used to send GET requests to the backend.
		$existing_studies = $request_handler->search_studies(
			Biobank_Admin::ITEMS_PER_PAGE,
			max(1, isset($_GET['paged']) ? $_GET['paged'] : 1),
			$search);
		$_GET["error"] = empty($_GET["error"]) ? $existing_studies->error : $_GET["error"];

		$studies = $existing_studies->data;
		$total_studies = isset($existing_studies->total) ? $existing_studies->total : 0;

		$pagination = $this->setup_pagination($total_studies);

		/*
		 * Fetch the study if an ID is given.
		 */
		if (isset($_GET["study_id"])) {
			$study_id = (int) $_GET["study_id"];
			$study_info = $request_handler->get_study($study_id);
			/*
			 * If an error arises, switch to the creation workflow.
			 */
			if (! empty($study->error)) {
				$action = "create";
				if (empty($error)) {
					$error = $study->error;
				}
			} else {
				$study = $study_info->study; // extract the study

				/*
				 * Extract the researchers, loading their information from WordPress.
				 */
				$study_researchers_info = $study_info->researchers;
				$study_researchers = array();
				foreach ($study_researchers_info as $researcher) {
					$study_researchers[$researcher->user_id] = get_user_by("login", $researcher->user_id)->display_name;
				}
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

		$plugin_page = $_GET["page"];
		$admin_page = "admin.php?page=$plugin_page";

		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-studies.php");
	}

	/**
	 * Display the study viewing page.
	 * This page is accessible only to researchers.
	 *
	 * @since	1.0.0
	 */
	public function display_view_studies_page() {
		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-study-info.php");
	}

	/**
	 * Display the emails page.
	 *
	 * @since	1.0.0
	 */
	public function display_emails_page() {
		include(plugin_dir_path(__FILE__) . "../includes/globals.php");

		/*
		 * Fetch existing emails by searching in their names and descriptions.
		 */
		$request_handler = new \client\form\EmailFormHandler(); // used to send GET requests to the backend.
		$existing_emails = $request_handler->search_emails(
			Biobank_Admin::ITEMS_PER_PAGE,
			max(1, isset($_GET['paged']) ? $_GET['paged'] : 1),
			isset($_GET["search"]) ? $_GET["search"] : "");
		$_GET["error"] = empty($_GET["error"]) ? $existing_emails->error : $_GET["error"];

		$emails = $existing_emails->data;
		$total_emails = isset($existing_emails->total) ? $existing_emails->total : 0;
		$pagination = $this->setup_pagination($total_emails);

		$plugin_page = $_GET["page"];
		$admin_page = "admin.php?page=$plugin_page";

		wp_enqueue_script( $this->plugin_name . "-email", plugin_dir_url( __FILE__ ) . 'js/biobank-email.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name . "-fontawesome", $fontawesome_kit, array( 'jquery' ), $this->version, false );
		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-emails.php");
	}

	/**
	 * Display the settings page.
	 *
	 * @since	1.0.0
	 */
	public function display_settings_page() {
		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-settings.php");
	}

	/**
	 * Encrypt the user's email address.
	 *
	 * @since	1.0.0
	 * @param	string	$user_id	The user's ID.
	 */
	public function encrypt_email($user_id) {
		global $wpdb;
		$user = get_user_by("id", $user_id);

		if (in_array("participant", $user->roles)) {
			/*
			 * Only encrypt the email address of research partners.
			 */
			require(plugin_dir_path(__FILE__) . "../includes/globals.php");
			$nonce = random_bytes(SODIUM_CRYPTO_SECRETBOX_NONCEBYTES);
			$cipherEmail = sodium_crypto_secretbox($user->data->user_email, $nonce, $encryptionKey);
			$encodedEmail = base64_encode($nonce . $cipherEmail);

			$wpdb->update(
				'wp_users',
				array(
					'user_email' => $encodedEmail
				),
				array( 'ID' => $user_id ),
				array(
					'%s'
				),
				array( '%d' )
			);
		}
	}

	/**
	 * Before sending an email, decrypt the user's email address if need be.
	 *
	 * @since	1.0.0
	 * @param	string	args	The email's data.
	 */
	public function before_email($args) {
		$user = get_user_by("email", $args['to']);

		if (in_array("participant", $user->roles)) {
			/*
			 * Only decrypt the email address of research partners.
			 */
			require(plugin_dir_path(__FILE__) . "../includes/globals.php");
			$decoded = base64_decode($user->data->user_email);
			$cipherNonce = mb_substr($decoded, 0, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, '8bit');
			$cipherText = mb_substr($decoded, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, null, '8bit');
			$email = sodium_crypto_secretbox_open($cipherText, $cipherNonce, $encryptionKey);

			$new_wp_mail = array(
				'to'          => $email,
				'subject'     => $args['subject'],
				'message'     => $args['message'],
				'headers'     => $args['headers'],
				'attachments' => $args['attachments'],
			);

			return $new_wp_mail;
		} else {
			return $args;
		}
	}

	/**
	 * Refresh the page, prettifying the URL.
	 * In the redirection, the GET parameters are stored in the session.
	 * Use with caution.
	 *
	 * @since	1.0.0
	 */
	public function redirect() {
		global $pagenow;

		if (session_status() == PHP_SESSION_NONE) {
		    session_start();
		}

	    if ($pagenow == "admin.php") {
			if (isset($_SESSION["redirected"])) {
				if ($_SESSION["redirected"]) {
					$_SESSION["redirected"] = false;
				}
			} else if (isset($_GET["page"]) && in_array($_GET["page"], $this->menu_pages) && count($_GET) > 1) {
				session_unset();
				$_SESSION = $_GET;
				$_SESSION["redirected"] = true;
				wp_redirect(admin_url( "/admin.php?page=" . $_GET["page"]), 301 );
				exit;
			}
	    }
	}

	/**
	 * Register the stylesheets for the admin area.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_styles() {

		/**
		 * This function is provided for demonstration purposes only.
		 *
		 * An instance of this class should be passed to the run() function
		 * defined in Biobank_Loader as all of the hooks are defined
		 * in that particular class.
		 *
		 * The Biobank_Loader will then create the relationship
		 * between the defined hooks and the functions defined in this
		 * class.
		 */

		 /*
 		 * Load the general UI.
 		 */
		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . "css/biobank-admin.css", array(), $this->version, "all" );

		/*
		 * Load the custom UI for each page.
		 */
		switch (get_current_screen()->id) {
			case "biobank_page_biobank_studies":
				wp_enqueue_style("jquery-ui-css", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.2/themes/smoothness/jquery-ui.css");
				wp_enqueue_style($this->plugin_name, plugin_dir_url( __FILE__ ) . "css/biobank-ui.css", array(), $this->version, "all");
				break;
			case "biobank_page_biobank_emails":
				wp_enqueue_style($this->plugin_name . "-email-style", plugin_dir_url( __FILE__ ) . "css/biobank-email.css", array(), $this->version, "all");
				break;
		}

	}

	/**
	 * Register the JavaScript for the admin area.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_scripts() {

		/**
		 * This function is provided for demonstration purposes only.
		 *
		 * An instance of this class should be passed to the run() function
		 * defined in Biobank_Loader as all of the hooks are defined
		 * in that particular class.
		 *
		 * The Biobank_Loader will then create the relationship
		 * between the defined hooks and the functions defined in this
		 * class.
		 */

		/*
		 * The basic scripts are always included.
		 */
		wp_enqueue_script("jquery-ui-datepicker");
		wp_enqueue_script($this->plugin_name, plugin_dir_url( __FILE__ ) . "js/biobank-admin.js", array("jquery", "jquery-ui-core", "jquery-ui-datepicker"), $this->version, false );

		wp_enqueue_script("user-profile");
		wp_enqueue_script("password-strength-meter");

		wp_enqueue_script("form", plugin_dir_url( __FILE__ ) . "js/forms/fields/decremental_select.js", array(), $this->version, false );

		if (get_current_screen()->id == "biobank_page_biobank_studies") {
			wp_enqueue_script("decremental_select", plugin_dir_url( __FILE__ ) . "js/forms/fields/decremental_select.js", array("jquery", "jquery-ui-core", "jquery-ui-datepicker"), $this->version, false );
			wp_enqueue_script("triple", plugin_dir_url( __FILE__ ) . "js/forms/fields/triple.js", array("jquery", "jquery-ui-core", "jquery-ui-datepicker"), $this->version, false );
		}
	}

	/**
	 * Options.
	 */

	/**
	 * A function called when the options have been updated.
	 *
	 * @since 1.0.0
	 * @access public
	 */
	public function options_update() {
		register_setting($this->plugin_name, $this->plugin_name, array($this, "validate_options"));
	}

	/**
	 * Validate the options.
	 *
	 * @since 1.0.0
	 * @access	public
	 * @param	array 		$input		The inputed options.
	 * @return	array		The array containing the validated inputs.
	 */
	public function validate_options($input) {
		$valid = array();

		$valid[$this->plugin_name . "-scheme"] = isset($input["scheme"]) && !empty($input["scheme"]) ? $input["scheme"] : "http";
		$valid[$this->plugin_name . "-host"] = isset($input["host"]) && !empty($input["host"]) ? $input["host"] : "localhost";
		$valid[$this->plugin_name . "-port"] = isset($input["port"]) && !empty($input["port"]) ? $input["port"] : "8080";

		return $valid;
	}

	/**
	 * Set up the pagination.
	 *
	 * @since	1.0.0
	 * @access	private
	 * @param	int		$total The total number of items, used to calculate the number of pages.
	 * @return	array	The array containing the pagination data.
	 */
	private function setup_pagination($total) {
		/*
		 * Pagination setup
		 */
		$page = max(1, isset($_GET['paged']) ? $_GET['paged'] : 1); // get the current page number
		$items_per_page = Biobank_Admin::ITEMS_PER_PAGE; // the number of items per page
		$search = isset($_GET["search"]) ? $_GET["search"] : ""; // get the search string

		$big = 999999999; // need an unlikely integer
		$pagination = (paginate_links( array(
			"base" => str_replace( $big, "%#%", get_pagenum_link( $big, false ) ),
			"format" => "?paged=%#%",
			"add_fragment" => empty($search) ? "" : "&search=$search",
			"current" => $page,
			"total" => ceil($total / $items_per_page)
		)));
		return $pagination;
	}

}
