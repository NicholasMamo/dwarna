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

require_once(plugin_dir_path(__FILE__) . "globals.php");

class Biobank_Activator {

    /**
     * Activate the biobank plugin.
     *
     * When the biobank plugin is activated, the biobank's user roles are created.
     * Capabilities are created for these users.
     * Biobanker permissions are applied to administrators as well.
     *
     * @since    1.0.0
     */
    public static function activate() {
        global $all_capabilities;

        /*
         * Create the user roles and associated capabilities
         */

		add_role("biobanker", "Biobanker", array()); // capabilities will be added alongside the administrator's
		add_role("researcher", "Researcher", array(
			"biobank_view_consent" => true,
            "biobank_view_admin_menu" => true,
		));
		add_role("participant", "Participant", array(
			"biobank_view_profile" => true,
            "biobank_view_admin_menu" => false,
		));

        /*
         * Mirror the biobanker's capbabilities to the administrator
         */

        $administrator = get_role("administrator");
        $biobanker = get_role("biobanker");
        foreach ($all_capabilities as $capability) {
            $administrator->add_cap($capability, true);
            $biobanker->add_cap($capability, true);
        }
    }

}
