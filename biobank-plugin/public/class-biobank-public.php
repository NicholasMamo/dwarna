<?php

require_once(plugin_dir_path(__FILE__) . "../client/form/consent_form_handler.php");

/**
 * The public-facing functionality of the plugin.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/public
 */

/**
 * The public-facing functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the public-facing stylesheet and JavaScript.
 *
 * @package    Biobank
 * @subpackage Biobank/public
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class Biobank_Public {

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
	 * @param      string    $plugin_name       The name of the plugin.
	 * @param      string    $version    The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

	}

	/**
	 * Register the stylesheets for the public-facing side of the site.
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

		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/biobank-public.css', array(), $this->version, 'all' );
		wp_enqueue_style( $this->plugin_name . "-bootstrap", 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css', array(), $this->version, 'all' );

	}

	/**
	 * Register the JavaScript for the public-facing side of the site.
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

		wp_enqueue_script( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/biobank-public.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name . "-form-verification", plugin_dir_url( __FILE__ ) . 'js/forms/verification.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name . "-popper", 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name . "-bootstrap", 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name . "-jszip", plugin_dir_url( __FILE__ ) . 'js/jszip/dist/jszip.js', array( 'jquery' ), $this->version, false );
	}

	/**
	 * On page initialization, check whether the action is linked to any handler.
	 * If it is, delegate the processing to that function.
	 * Otherwise do nothing.
	 *
	 * The function looks for the action in the GET parameters.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function init() {
		$this->is_authorized();

		/*
		 * If there is no set study ID in the session, then redirect to the homepage.
		 * TODO: Check for the study ID in the parameter, and handle consent another way (maybe authenticate and then refresh).
		 */
		if (strpos($_SERVER['REQUEST_URI'], 'biobank-study') && ! isset($_SESSION['study_id'])) {
			wp_redirect(get_site_url());
			exit;
		}

		$action = $_GET['action'] ?? NULL;
		if ($action) {
			switch ($action) {
				case 'consent':
					// (new \client\form\ConsentFormHandler())->save_consent();
					break;
			}
		}
	}

	/**
	 * Register the shortcodes that appear in the public-facing side of the site.
	 *
	 * @since    1.0.0
	 * @access	public
	 */
	public function register_shortcodes() {
		add_shortcode("biobank-consent", array($this, "display_consent_form"));
		add_shortcode("biobank-study", array($this, "display_study"));
		add_shortcode("biobank-trail", array($this, "display_consent_trail"));
	}

	/**
	 * Show the consent trail page.
	 *
	 * @since    1.0.0
	 * @access	public
	 * @param	string		$content		The content that is provided along the shortcode.
	 */
	public function display_consent_trail($content=NULL) {
		/*
		 * This view should only be displayed if the user is logged in and they are a participant.
		 */
		if (\is_user_logged_in()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				include_once(plugin_dir_path(__FILE__) . "partials/biobank-public-trail.php");
			}
		}
	}

	/**
	 * Show the study page.
	 *
	 * @since    1.0.0
	 * @access	public
	 */
	public function display_study() {
		/*
		 * This view should only be displayed if the user is logged in, they are a participant and there is a study stored in the session.
		 */
		if (\is_user_logged_in()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				if (isset($_SESSION['study_id']) &&
					isset($_GET['action']) && $_GET['action'] == 'consent') {
					wp_enqueue_script( $this->plugin_name . "-hyperledger-card", plugin_dir_url( __FILE__ ) . 'js/hyperledger/card.js', array( 'jquery' ), $this->version, false );

					$consent_handler = new \client\form\ConsentFormHandler();
					$error = '';

					/*
					 * Load the timeline in chronological order.
					 */
					$trail = $consent_handler->get_consent_trail();
					$error = isset($trail->error) && ! empty($trail->error) ? $trail->error : $error;
					$studies = (array) $trail->studies;
					$timeline = (array) $trail->timeline;
					ksort($timeline);

					/*
					 * Load the quiz.
					 */
					wp_enqueue_script( $this->plugin_name . "-quiz", plugin_dir_url( __FILE__ ) . 'js/quiz.js', array( 'jquery' ), $this->version, false );
					$contents = file_get_contents(plugin_dir_path(__FILE__) . 'data/quiz.json');
					$quiz = json_decode($contents);

					/*
					 * TODO: Create a new function.
					 */
					$studies = (new \client\form\ConsentFormHandler())->get_active_studies();
					foreach ($studies->data as $study) {
						if ($study->study->study_id == $_SESSION['study_id']) {
							include_once(plugin_dir_path(__FILE__) . "partials/components/study.php");
							break;
						}
					}
				}
			}
		}
	}

	/**
	 * Show the consent form page.
	 *
	 * @since    1.0.0
	 * @access	public
	 * @param	string		$content		The content that is provided along the shortcode.
	 */
	public function display_consent_form($content=NULL) {
		/*
		 * This view should only be displayed if the user is logged in and they are a participant.
		 */
		if (\is_user_logged_in()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				wp_enqueue_script( $this->plugin_name . "-hyperledger-card", plugin_dir_url( __FILE__ ) . 'js/hyperledger/card.js', array( 'jquery' ), $this->version, false );

				$consent_handler = new \client\form\ConsentFormHandler();
				$active_studies = $consent_handler->get_active_studies();
				$error = "";
				$error = isset($active_studies->error) && ! empty($active_studies->error) ? $active_studies->error : $error;

				/*
				 * Extract a list of studies that are active.
				 * These will later be used to separate consented studies from non-consented ones.
				 */
				$all_studies = array();
				foreach ($active_studies->data as $study) {
					array_push($all_studies, $study->study->study_id);
				}

				include_once(plugin_dir_path(__FILE__) . "partials/biobank-public-consent.php");
			}
		}
	}

	/**
	 * Check whether the user has authorized.
	 * If they are not authorized, redirect them to authorize themselves.
	 *
	 * The function checks that the user is a participant.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function is_authorized() {
		include(plugin_dir_path(__FILE__) . "../includes/globals.php");

		$roles = (array) wp_get_current_user()->roles;

		/*
		 * If the user is logged in and they are a participant, they are redirected to authorize themselves.
		 * Otherwise, if they are not logged in, they are considered to be unauthorized.
		 */
		if (\is_user_logged_in()
			&& in_array("participant", $roles)
			&& ! is_admin()) {
			if (isset($_GET["authorized"]) && $_GET["authorized"]) {
				$_SESSION["authorized"] = true;
			} else if (!isset($_SESSION["authorized"]) && !isset($_GET["redirect_uri"])) {
				wp_redirect($auth_url);
				exit;
			}
		} else if (!\is_user_logged_in()) {
			unset($_SESSION["authorized"]);
		}
	}

	/**
	 * A filter function that modifies the visibility of certain menu pages.
	 * This can be used to filter out pages that are not
	 */
	public function set_menu_visibility($items, $menu, $args) {
		include(plugin_dir_path(__FILE__) . "../includes/globals.php");
		foreach ($items as $id => $item) {
			/*
			 * Load the actual post.
			 * Menus create their own pages, which they then redirect.
			 */
			$post = get_post($item->object_id);
			$slug = $post->post_name;
			if (array_key_exists($slug, $plugin_pages)) {
				/*
				 * If the page was created by the plugin, check whether the user has the necessary permissions to view it.
				 * If they do not, remove the menu item from view.
				 */
				if (\is_user_logged_in()) {
					$user = wp_get_current_user();
					$role = $user->roles[0];
					if (! in_array($role, $plugin_pages[$slug]["permissions"])) {
						unset($items[$id]);
					}
				}
			}
		}
		return $items;
	}

	/**
	 * Get the blockchain solution's access token.
	 * It is assumed that this access token is stored in a cookie.
	 */
	public function get_blockchain_access_token() {
		require(plugin_dir_path(__FILE__) . "../includes/globals.php");
		$access_token = $_COOKIE[$blockchain_access_token];
		// A Hyperledger Composer access token looks like this:
		// s:05xpfhY0HIrDzs53FeqgYJ47oP5swGnZLsvHD2aWAwN52trpfPCEViJaTcSQ9LfC.Q1kYwi0cRB9T47G/fN0RzDXyLoh0hb1XDqnKMkkh40A
		$access_token = substr($access_token, 2, strpos($access_token, '.') - 2);
		return $access_token;
	}

}
