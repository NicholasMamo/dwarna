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

require_once(plugin_dir_path(__FILE__) . "globals.php");

class Biobank_Deactivator {

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
		global $all_capabilities;

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
        foreach ($all_capabilities as $capability) {
			$administrator->remove_cap($capability, false);
        }

	}

}
