<?php

/**
 * Fired during plugin activation
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/includes
 */

/**
 * Fired during plugin activation.
 *
 * This class defines all code necessary to run during the plugin's activation.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/includes
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */

class Biobank_Activator {

    /**
     * The full list of capabilities afforded by the biobank plugin.
	 * This list is given both to the biobanker, and to the administrator.
     *
     * @since	1.0.0
	 * @access   protected
	 * @var      array		$biobanker_capabilities    The full list of capabilities afforded by the biobank plugin to biobankers and administrators.
     */
    protected static $biobanker_capabilities = array();

    /**
     * The permissions given to researchers by the biobank plugin.
     *
     * @since	1.0.0
	 * @access   protected
	 * @var      array		$biobanker_capabilities    The full list of capabilities afforded by the biobank plugin to researchers.
     */
    protected static $researcher_capabilities = array();

    /**
     * The permissions given to participants by the biobank plugin.
     *
     * @since	1.0.0
	 * @access   protected
	 * @var      array		$biobanker_capabilities    The full list of capabilities afforded by the biobank plugin to participants.
     */
    protected static $participant_capabilities = array();

    /**
     * The list of pages created by the biobank plugin.
	 * These pages are made up of WordPress information and permissions.
     *
     * @since	1.0.0
	 * @access   protected
	 * @var      array		$pages    The list of pages that are created by the biobank plugin.
     */
    protected static $pages = array();

    /**
     * Since the static members of this class use the capabilities, they are imported as static variables.
     *
     * @since	1.0.0
     * @access	private
     */
    private static function initialize() {
		require(plugin_dir_path(__FILE__) . "globals.php");
		self::$biobanker_capabilities = $biobanker_capabilities;
        self::$researcher_capabilities = $researcher_capabilities;
		self::$participant_capabilities = $participant_capabilities;
		self::$pages = $plugin_pages;
    }

	/**
	 * Set up the OAuth 2.0 tables from the database.
	 */
	private static function create_oauth_tables() {
		global $wpdb;
		$install_script = file_get_contents(plugin_dir_path(__FILE__) . "../oauth2/install.sql");
		$queries = preg_split("/;\n/", $install_script);
		foreach ($queries as $query) {
			if (strlen($query)) {
				$wpdb->query($query, array());
			}
		}
	}

    /**
     * Activate the biobank plugin.
     *
     * When the biobank plugin is activated, the biobank's user roles are created.
     * Capabilities are created for these users.
     * Biobanker permissions are applied to administrators as well.
     *
     * @since	1.0.0
     */
    public static function activate() {
        self::initialize();

        /*
         * Create the user roles.
         */

		add_role("biobanker", "Biobanker", array());
		add_role("researcher", "Researcher", array());
		add_role("participant", "Participant", array());

        /*
		 * Add the role capabilities.
         * Mirror the biobanker's capbabilities to the administrator.
         */

        $administrator = get_role("administrator");
        $biobanker = get_role("biobanker");
        foreach (self::$biobanker_capabilities as $capability) {
            $administrator->add_cap($capability, true);
            $biobanker->add_cap($capability, true);
        }

		$researcher = get_role("researcher");
		foreach (self::$researcher_capabilities as $capability) {
			$researcher->add_cap($capability, true);
		}

		$participant = get_role("participant");
		foreach (self::$participant_capabilities as $capability) {
			$participant->add_cap($capability, true);
		}

		/*
		 * Create the frontend pages.
		 */
		foreach (self::$pages as $slug => $page) {
			$post = wp_insert_post($page["wp_info"]);
		}

		/**
		 * Register the default options.
		 */
		self::register_default_options();

		/*
		 * Create the OAuth 2.0 table structure in the the database.
		 */
		 self::create_oauth_tables();
    }

	/**
	 * Set the initial settings.
	 *
	 * @access	private
     * @since	1.0.0
	 */
	private static function register_default_options() {
		require(plugin_dir_path(__FILE__) . "globals.php");

		$plugin_name = 'biobank';

		$rest_settings = get_option("$plugin_name-rest");
		if (! is_array($rest_settings)) {
			$rest_settings = is_array($rest_settings) ? $rest_settings : array();
			$rest_settings["$plugin_name-rest"] = $default_rest_settings;
		} else {
			foreach ($default_rest_settings as $setting => $default_value) {
				$rest_settings["$plugin_name-rest"][$setting] = $rest_settings["$plugin_name-rest"][$setting] ?? $default_value;
			}
		}
		add_option("$plugin_name-rest", $rest_settings["$plugin_name-rest"]);

		$composer_settings = get_option("$plugin_name-composer");
		if (! is_array($composer_settings)) {
			$composer_settings = is_array($composer_settings) ? $composer_settings : array();
			$composer_settings["$plugin_name-composer"] = $default_composer_settings;
		} else {
			foreach ($default_composer_settings as $setting => $default_value) {
				$composer_settings["$plugin_name-composer"][$setting] = $composer_settings["$plugin_name-composer"][$setting] ?? $default_value;
			}
		}
		add_option("$plugin_name-composer", $composer_settings["$plugin_name-composer"]);
	}

}
