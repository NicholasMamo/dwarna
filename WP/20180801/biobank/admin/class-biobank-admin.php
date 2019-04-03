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
	 * Initialize the class and set its properties.
	 *
	 * @since    1.0.0
	 * @param      string    $plugin_name       The name of this plugin.
	 * @param      string    $version    The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

	}

	/**
	 * Add the biobank menu to the side menu
	 *
	 * @since	1.0.0
	 */
	public function add_plugin_admin_menu() {
		$top_level_slug = "biobank_main";

		/*
		 * Add the top-level menu
		 */

		add_menu_page(
			"Biobank Management",
			"Biobank",
			"biobank_view_admin_menu",
			$top_level_slug
		);

		/*
		 * Add all the sub-menus
		 */

		add_submenu_page(
			$top_level_slug,
			"Manage Participants",
			"Participants",
			"biobank_create_participant",
			"biobank_participants",
			array($this, "display_participants_page")
		);

	   add_submenu_page(
		   $top_level_slug,
		   "Manage Researchers",
		   "Researchers",
		   "biobank_create_researcher",
		   "biobank_researchers",
		   array($this, "display_researchers_page")
	   );
	}

	public function display_participants_page() {
		include_once(plugin_dir_path(__FILE__) . "partials/biobank-admin-participants.php");
	}

	public function display_researchers_page() {
		echo "researchers";
	}

	/*
	 * Validation
	 */

	public function participants_update() {
		register_setting($this->plugin_name . "-participants", "participant", array($this, "validate_participant"));
	}

	public function validate_participant($input) {
		$valid = array();

		if (empty($input["username"])) {
			add_settings_error(
		        $this->plugin_name . "-participants",
		        'login_background_color_texterror',
		        'Please enter a valid username',
		        'error'
	        );
		} else {
			$valid["username"] = $input["username"];
		}

		return false;
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

		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/biobank-admin.css', array(), $this->version, 'all' );

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

		wp_enqueue_script( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/biobank-admin.js', array( 'jquery' ), $this->version, false );

	}

}
