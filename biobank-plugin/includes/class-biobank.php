<?php

/**
 * The file that defines the core plugin class
 *
 * A class definition that includes attributes and functions used across both the
 * public-facing side of the site and the admin area.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/includes
 */

require_once(plugin_dir_path(__FILE__) . "../client/form/consent_form_handler.php");
require_once(plugin_dir_path(__FILE__) . "../client/form/study_form_handler.php");
require_once(plugin_dir_path(__FILE__) . "../client/form/user_form_handler.php");

/**
 * The core plugin class.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 *
 * Also maintains the unique identifier of this plugin as well as the current
 * version of the plugin.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/includes
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class Biobank {

	/**
	 * The loader that's responsible for maintaining and registering all hooks that power
	 * the plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      Biobank_Loader    $loader    Maintains and registers all hooks for the plugin.
	 */
	protected $loader;

	/**
	 * The unique identifier of this plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      string    $plugin_name    The string used to uniquely identify this plugin.
	 */
	protected $plugin_name;

	/**
	 * The current version of the plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      string    $version    The current version of the plugin.
	 */
	protected $version;

	/**
	 * Define the core functionality of the plugin.
	 *
	 * Set the plugin name and the plugin version that can be used throughout the plugin.
	 * Load the dependencies, define the locale, and set the hooks for the admin area and
	 * the public-facing side of the site.
	 * The form handler for the plugin is also created here
	 *
	 * @since    1.0.0
	 */
	public function __construct() {
		if ( defined( 'PLUGIN_NAME_VERSION' ) ) {
			$this->version = PLUGIN_NAME_VERSION;
		} else {
			$this->version = '1.0.0';
		}
		$this->plugin_name = 'biobank';

		$this->load_dependencies();
		$this->set_locale();
		$this->define_admin_hooks();
		$this->define_public_hooks();

	}

	/**
	 * Load the required dependencies for this plugin.
	 *
	 * Include the following files that make up the plugin:
	 *
	 * - Biobank_Loader. Orchestrates the hooks of the plugin.
	 * - Biobank_i18n. Defines internationalization functionality.
	 * - Biobank_Admin. Defines all hooks for the admin area.
	 * - Biobank_Public. Defines all hooks for the public side of the site.
	 *
	 * Create an instance of the loader which will be used to register the hooks
	 * with WordPress.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function load_dependencies() {

		/**
		 * The class responsible for orchestrating the actions and filters of the
		 * core plugin.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-biobank-loader.php';

		/**
		 * The class responsible for defining internationalization functionality
		 * of the plugin.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-biobank-i18n.php';

		/**
		 * The class responsible for defining all actions that occur in the admin area.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-biobank-admin.php';

		/**
		 * The class responsible for defining all actions that occur in the public-facing
		 * side of the site.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-biobank-public.php';

		$this->loader = new Biobank_Loader();

	}

	/**
	 * Define the locale for this plugin for internationalization.
	 *
	 * Uses the Biobank_i18n class in order to set the domain and to register the hook
	 * with WordPress.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function set_locale() {

		$plugin_i18n = new Biobank_i18n();

		$this->loader->add_action( 'plugins_loaded', $plugin_i18n, 'load_plugin_textdomain' );

	}

	/**
	 * Register all of the hooks related to the admin area functionality
	 * of the plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function define_admin_hooks() {

		$plugin_admin = new Biobank_Admin( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_styles' );
		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_scripts' );

		$this->loader->add_action( 'admin_init', $plugin_admin, 'redirect' ); // to prettify URLs - places GET parameters in session
		$this->loader->add_action( 'admin_menu', $plugin_admin, 'add_plugin_admin_menu' );
		$this->loader->add_action( 'admin_init', $plugin_admin, 'options_update' );

		/*
		 * Participant forms
		 */
		$participant_form_handler = new \client\form\ParticipantFormHandler();
		$this->loader->add_action( 'admin_post_create_participant', $participant_form_handler, 'create_participant' );
		$this->loader->add_action( 'admin_post_update_participant', $participant_form_handler, 'update_participant' );
		$this->loader->add_action( 'admin_post_remove_participant', $participant_form_handler, 'remove_participant' );

		/*
		 * Researcher forms
		 */
		$researcher_form_handler = new \client\form\ResearcherFormHandler();
 		$this->loader->add_action( 'admin_post_create_researcher', $researcher_form_handler, 'create_researcher' );
 		$this->loader->add_action( 'admin_post_update_researcher', $researcher_form_handler, 'update_researcher' );
 		$this->loader->add_action( 'admin_post_remove_researcher', $researcher_form_handler, 'remove_researcher' );

		/*
		 * Study forms
		 */
		$study_form_handler = new \client\form\StudyFormHandler();
		$this->loader->add_action( 'admin_post_create_study', $study_form_handler, 'create_study' );
		$this->loader->add_action( 'admin_post_update_study', $study_form_handler, 'update_study' );
		$this->loader->add_action( 'admin_post_remove_study', $study_form_handler, 'remove_study' );

		/*
		 * Consent forms
		 */
		$consent_form_handler = new \client\form\ConsentFormHandler();
		$this->loader->add_action( 'admin_post_consent_form', $consent_form_handler, 'update_consent' );

		$this->loader->add_action( 'user_register', $plugin_admin, 'encrypt_email' );
		$this->loader->add_action( 'wp_mail', $plugin_admin, 'before_email' );
	}

	/**
	 * Register all of the hooks related to the public-facing functionality
	 * of the plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function define_public_hooks() {

		$plugin_public = new Biobank_Public( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_styles' );
		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_scripts' );

		$this->loader->add_action( 'init', $plugin_public, 'register_shortcodes' );
		$this->loader->add_action( 'init', $plugin_public, 'is_authorized' );

		$this->loader->add_filter( 'wp_get_nav_menu_items', $plugin_public, 'set_menu_visibility', 10, 3 );

	}

	/**
	 * Run the loader to execute all of the hooks with WordPress.
	 *
	 * @since    1.0.0
	 */
	public function run() {
		$this->loader->run();
	}

	/**
	 * The name of the plugin used to uniquely identify it within the context of
	 * WordPress and to define internationalization functionality.
	 *
	 * @since     1.0.0
	 * @return    string    The name of the plugin.
	 */
	public function get_plugin_name() {
		return $this->plugin_name;
	}

	/**
	 * The reference to the class that orchestrates the hooks with the plugin.
	 *
	 * @since     1.0.0
	 * @return    Biobank_Loader    Orchestrates the hooks of the plugin.
	 */
	public function get_loader() {
		return $this->loader;
	}

	/**
	 * Retrieve the version number of the plugin.
	 *
	 * @since     1.0.0
	 * @return    string    The version number of the plugin.
	 */
	public function get_version() {
		return $this->version;
	}

}
