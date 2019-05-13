<?php

/**
 * Fired during plugin deactivation
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/includes
 */

/**
 * Fired during plugin deactivation.
 *
 * This class defines all code necessary to run during the plugin's deactivation.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/includes
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */

class Biobank_Deactivator {

    /**
     * The full list of capabilities afforded by the biobank plugin.
	 * This list is given both to the biobanker, and to the administrator.
     *
     * @since    1.0.0
     */
    protected static $biobanker_capabilities = array();

    /**
     * The list of pages created by the biobank plugin.
	 * These pages are made up of WordPress information and permissions.
     *
     * @since    1.0.0
	 * @access   protected
	 * @var      array		$biobanker_capabilities    The list of pages that are created by the biobank plugin.
     */
    protected static $pages = array();

    /**
     * Since the static members of this class use the capabilities, they are imported as static variables
     *
     * @since	1.0.0
     * @access	private
     */
    private static function initialize() {
		require(plugin_dir_path(__FILE__) . "globals.php");
		self::$biobanker_capabilities = $biobanker_capabilities;
		self::$pages = $plugin_pages;
    }

	/**
	 * Drop the OAuth 2.0 tables from the database.
	 */
	private static function drop_oauth_tables() {
		global $wpdb;
		$uninstall_script = file_get_contents(plugin_dir_path(__FILE__) . "../oauth2/uninstall.sql");
		$queries = preg_split("/;\n/", $uninstall_script);
		foreach ($queries as $query) {
			if (strlen($query)) {
				$wpdb->query($query, array());
			}
		}
	}

	/**
	 * Clean up when the biobank plugin is deactivated.
	 *
	 * When the biobank plugin is deactivated, the activation actions have to be rolled back.
	 * The user roles are removed since they serve no additional use.
	 * User capabilities are removed as wel..
	 *
	 * @since    1.0.0
	 */
	public static function deactivate() {
		self::initialize();

		/*
		 * Remove the user roles
		 */
		remove_role("biobanker");
		remove_role("researcher");
		remove_role("participant");

		/*
		 * Remove the additional capabilities added to the administrator
		 */
		$administrator = get_role("administrator");
        foreach (self::$biobanker_capabilities as $capability) {
			$administrator->remove_cap($capability, false);
        }

		/*
		 * Remove the page created by the plugin.
		 * Remove any page with the correct slug - there may be old ones still active.
		 */
		foreach (self::$pages as $slug => $plugin_page) {
			$plugin_pages = get_posts(array(
				"name" => $slug,
				"post_status" => "publish",
				"post_author" => 1,
				"post_type" => "page",
			));
			foreach($plugin_pages as $page) {
				wp_delete_post($page->ID, true); // forcefully remove it
			}
		}

		/*
		 * Remove any OAuth 2.0 data from the database.
		 */
		 self::drop_oauth_tables();
	}

}
