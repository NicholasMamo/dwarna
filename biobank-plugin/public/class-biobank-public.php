<?php

require_once(plugin_dir_path(__FILE__) . "../client/form/consent_form_handler.php");
require_once(plugin_dir_path(__FILE__) . "../client/form/email_form_handler.php");

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
		include(plugin_dir_path(__FILE__) . "../includes/globals.php");
		$this->is_authorized();

		/*
		 * If the user is trying to access a study page without having a study ID in the session, then redirect to the homepage.
		 */
		if (strpos($_SERVER['REQUEST_URI'], $plugin_pages['biobank-study']['wp_info']['post_name']) && ! isset($_SESSION['study_id'])) {
			wp_redirect(get_site_url());
			exit;
		}

		/*
		 * If the user is trying to access the consent page but they are not logged in, redirect to the login page.
		 */
		if (isset($_GET['page_id'])){
			$page = get_post($_GET['page_id']);
			$slug = $page->post_name;
		} else {
			$slug = $_SERVER['REQUEST_URI'];
		}

		/*
		 * Compare the slug with the consent page's slug if the user is not already trying to log in or if they are not logged.
		 */
		$consent_slug = $plugin_pages['biobank-consent']['wp_info']['post_name'];
		$login_page = get_option("{$this->plugin_name}-other")['login'];
		if ((strpos($slug, $consent_slug) || $slug == $consent_slug) &&
			! strpos($_SERVER['REQUEST_URI'], $login_page) && ! is_user_logged_in()) {
			wp_redirect(home_url() . "/$login_page");
			exit;
		}

		$action = $_GET['action'] ?? NULL;
		if ($action) {
			switch ($action) {
				case 'consent':
					if (! isset($_GET[BLOCKCHAIN_ACCESS_TOKEN]) && ! strpos($_SERVER['REQUEST_URI'], 'get_cookie.php')) {
						wp_redirect(get_option('biobank-composer')['hyperledger-host'] .
									"?redirect=" . urlencode($_SERVER["REQUEST_SCHEME"] . "://" . $_SERVER["HTTP_HOST"] . $_SERVER["REQUEST_URI"]));
						exit;
					} else {
						setcookie(BLOCKCHAIN_ACCESS_TOKEN, $_GET[BLOCKCHAIN_ACCESS_TOKEN], time() + 3600, '/');
						$_COOKIE[BLOCKCHAIN_ACCESS_TOKEN] = $_GET[BLOCKCHAIN_ACCESS_TOKEN];
					}
					break;
			}
		}

		require(plugin_dir_path(__FILE__) . "../includes/globals.php");
		$slug = $this->get_current_slug();
		if (isset($plugin_pages[$slug])) {
			$page = $plugin_pages[$slug];
			if (! $page['public'] && ! is_user_logged_in()) {
				wp_redirect(home_url());
				exit;
			}
		}
	}

	/**
	 * When the user logs out, clear the study session variable.
	 * This fixes the issue of redirecting users to the study page even though they have not authenticated with Passport.js for that study.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function clear_session() {
		unset($_SESSION['study_id']);
		unset($_SESSION['authorized']);
	}

	/**
	 * When the user logs out, remove the Hyperledger Composer cookie.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function clear_access_token() {
		require(plugin_dir_path(__FILE__) . "../includes/globals.php");
		setcookie(BLOCKCHAIN_ACCESS_TOKEN, null, -1, '/');
		unset($_COOKIE[BLOCKCHAIN_ACCESS_TOKEN]);
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
		add_shortcode("biobank-subscription", array($this, "display_subscription_form"));
		add_shortcode("biobank-recruitment", array($this, "display_recruitment_form"));
		add_shortcode("biobank-erasure", array($this, "display_erasure_form"));
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
		if (\is_user_logged_in() && ! is_admin()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-trail.php");
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
		if (\is_user_logged_in() && ! is_admin()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				if (isset($_SESSION['study_id']) &&
					isset($_GET['action']) && $_GET['action'] == 'consent') {
					wp_enqueue_script( $this->plugin_name . "-hyperledger-config", plugin_dir_url( __FILE__ ) . 'js/ethereum/config.js', array( 'jquery' ), $this->version, false );
					wp_enqueue_script( $this->plugin_name . "-hyperledger-card", plugin_dir_url( __FILE__ ) . 'js/ethereum/card.js', array( 'jquery' ), $this->version, false );

					$consent_handler = new \client\form\ConsentFormHandler();
					$error = '';

					/*
					 * Load the timeline in chronological order.
					 */
					$trail = $consent_handler->get_consent_trail();
					$error = isset($trail->error) && ! empty($trail->error) ? $trail->error : $error;
					$studies = (array) $trail->studies;
					$timeline = (array) $trail->timeline;
					krsort($timeline);

					/*
					 * Load the quiz.
					 */
					wp_enqueue_script( $this->plugin_name . "-quiz", plugin_dir_url( __FILE__ ) . 'js/quiz.js', array( 'jquery' ), $this->version, false );
					$contents = file_get_contents(plugin_dir_path(__FILE__) . 'data/quiz.json');
					$quiz = json_decode($contents);

					/*
					 * Load the study.
					 */
					$study = (new \client\form\StudyFormHandler())->get_study($_SESSION['study_id']);
					include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-study.php");
					return;
				}
			}
		}

		/*
		 * If the function fails in some way, redirect to the homepage.
		 */
		if (! is_admin()) {
			wp_redirect(get_site_url());
			exit;
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
		if (\is_user_logged_in() && ! is_admin()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				wp_enqueue_script( $this->plugin_name . "-hyperledger-config", plugin_dir_url( __FILE__ ) . 'js/ethereum/config.js', array( 'jquery' ), $this->version, false );
				wp_enqueue_script( $this->plugin_name . "-hyperledger-card", plugin_dir_url( __FILE__ ) . 'js/ethereum/card.js', array( 'jquery' ), $this->version, false );

				$consent_handler = new \client\form\ConsentFormHandler();
				$active_studies = $consent_handler->get_active_studies();
				$error = "";

				$error = isset($active_studies->error) && ! empty($active_studies->error) ? $active_studies->error : $error;

				/*
				 * Non-recruiting studies are displayed apart.
				 */
				$non_recruiting_studies = array_filter((array) $active_studies->data,
													 function ($study) {
														 return ! $study->study->recruiting;
													 });
				$non_recruiting_studies = array_map(function ($study) {
														return $study->study;
													}, $non_recruiting_studies);
				$non_recruiting_study_ids = array_map(function ($study) {
													  	return $study->study->study_id;
													}, $non_recruiting_studies);
				$non_recruiting_study_ids = array_keys($non_recruiting_study_ids);

				/*
				 * Separate the consented studies.
				 */
				$consented_studies = $consent_handler->get_studies_by_participant();
				$consented_study_ids = array_map(function ($study) { return $study->study->study_id; },
												 $consented_studies->data);
				$consented_studies = array_map(function ($study) { return $study->study; },
											   (array) $consented_studies->data);
				$consented_studies = array_filter($consented_studies,
												  function ($study) use ($non_recruiting_study_ids) {
												  	return ! in_array($study->study_id, $non_recruiting_study_ids);
												  });

				$non_consented_studies = array_map(function ($study) { return $study->study; },
												   (array) $active_studies->data);
				$non_consented_studies = array_filter($non_consented_studies,
													  function ($study) use ($consented_study_ids, $non_recruiting_study_ids) {
														  return ! in_array($study->study_id, $consented_study_ids) &&
														  		 ! in_array($study->study_id, $non_recruiting_study_ids);
													  });
				include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-consent.php");
				return;
			}
		}

		/*
		 * If the function fails in some way, redirect to the homepage.
		 */
		if (! is_admin()) {
			wp_redirect(get_site_url());
			exit;
		}
	}

	/**
	 * Show the form that allows research partners to unsubscribe from or re-subscribe to receiving biobank-related emails.
	 *
	 * @since    1.0.0
	 * @access	public
	 */
	public function display_subscription_form() {
		if (\is_user_logged_in() && ! is_admin()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				$email_handler = new \client\form\EmailFormHandler();
				$subscriptions = $email_handler->get_subscriptions();
				$subscriptions->data = (object) $subscriptions->data;

				include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-subscription.php");
				return;
			}
		}

		/*
		 * If the function fails in some way, redirect to the homepage.
		 */
		if (! is_admin()) {
			wp_redirect(get_site_url());
			exit;
		}
	}

	/**
	 * Show the form that allows members of the general public to apply to become research partners.
	 *
	 * @since    1.0.0
	 * @access	public
	 */
	public function display_recruitment_form() {
		if (! \is_user_logged_in() && ! is_admin()) {
			include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-recruitment.php");
		}

		if (! is_admin()) {
			wp_redirect(get_site_url());
			exit;
		}
	}

	/**
	 * Show the form that allows research partners to erase all their data
	 *
	 * @since    1.0.0
	 * @access	public
	 */
	public function display_erasure_form() {
		if (\is_user_logged_in() && ! is_admin()) {
			$user = wp_get_current_user();
			$role = $user->roles[0];
			if ($role == "participant") {
				include_once(plugin_dir_path(__FILE__) . "../partials/public/biobank-public-erasure.php");
				return;
			}
		}

		/*
		 * If the function fails in some way, redirect to the homepage.
		 */
		if (! is_admin()) {
			wp_redirect(get_site_url());
			exit;
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
				$_SESSION["authorized"] = true;
			}

		} else if (!\is_user_logged_in()) {
			unset($_SESSION["authorized"]);
		}
	}

	/**
	 * A filter function that modifies the visibility of certain menu pages.
	 * This can be used to filter out pages that should not be accessible directly.
	 * Note that this affects only visibility, not access permissions.
	 *
	 * A page is shown if one of two conditions are reached.
	 *
	 * 	 1. The user is logged-in and they have the necessary credentials to read the page.
	 *	 2. The page is public, and is thus shown to every logged-out user.
	 *      For a plugin page to be shown to everyone, it has to be public and visible to all user roles.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	array	$items	The menu items.
	 * @param	object	$menu	The menu that is being loaded.
	 * @param	array	$args	Any other arguments.
	 * @return	array	The filtered menu items.
	 */
	public function set_menu_visibility($items, $menu, $args) {
		include(plugin_dir_path(__FILE__) . "../includes/globals.php");

		/*
		 * If this is an administration page, load all menu items normally.
		 * This fixes an issue whereby the menu items do not appear in the _Appearance -> Menus_ settings page in the administrator dashboard.
		 */
		if (is_admin()) {
			return $items;
		}

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
				 * If the user is not logged in and the page is not public, remove the menu item from view.
				 */
				if (\is_user_logged_in()) {
					$user = wp_get_current_user();
					$role = $user->roles[0];
					if (! count(array_intersect($user->roles, $plugin_pages[$slug]["menu_visibility"]))) {
						unset($items[$id]);
					}
				} else if (! $plugin_pages[$slug]["public"]) {
					unset($items[$id]);
				}
			}
		}
		return $items;
	}

	/**
	 * When a user attempts to log in, check if they are logging in using their email address.
	 * If they are, try to encrypt it in case this is a research partner.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string	$username	The username used to log in.
	 *								This can either be an actual username or an email address.
	 */
	public function encrypt_email_for_login(&$username) {
		/*
		 * Only proceed if the 'username' is actually an email address.
		 */
		if (is_email($username)) {
			/*
			 * If there is already a user associated with the given email address, proceed normally.
			 */
			if (get_user_by("email", $username)) {
				return;
			}

			/*
			 * Otherwise, hash the email address and check if any user has the same hashed email address.
			 */
			$users = get_users(array('meta_key' => 'hashed_email', 'meta_value' => hash('sha256', $username)));
			if (count($users)) {
				$username = $users[0]->data->user_login;
			}
		}
	}

	/**
	 * When a user attempts to reset their password, check if they provided their email address.
	 * If they did, try to encrypt it in case this is a research partner.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function encrypt_email_for_lost_password() {
		if (isset($_POST['user_login'])) {
			$username = $_POST['user_login'];
			/*
			 * Only proceed if the 'username' is actually an email address.
			 */
			if (is_email($username)) {
				/*
				 * If there is already a user associated with the given email address, proceed normally.
				 */
				if (get_user_by("email", $username)) {
					return;
				}

				/*
				 * Otherwise, hash the email address and check if any user has the same hashed email address.
				 * If there exists one, get that user and replace the input with the proper username.
				 */
				$users = get_users(array('meta_key' => 'hashed_email', 'meta_value' => hash('sha256', $username)));
				if (count($users)) {
					$_POST['user_login'] = $users[0]->data->user_login;
				}
			}
		}
	}

	/**
	 * After the user changes their password, send them an email confirming the change.
	 *
	 * @since 4.4.0
	 *
	 * @param WP_User $user     The user who changed their password.
	 */
	public function after_password_reset($user) {
		$email = $user->data->user_email;

		/*
		 * If the user's email address does not look like an email address, try to decrypt it.
		 */
		if (! is_email($email)) {
			require(plugin_dir_path(__FILE__) . "../includes/globals.php");
			$decoded = base64_decode($user->data->user_email);
			$cipherNonce = mb_substr($decoded, 0, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, '8bit');
			$cipherText = mb_substr($decoded, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, null, '8bit');
			$email = sodium_crypto_secretbox_open($cipherText, $cipherNonce, ENCRYPTION_KEY);
		}

		/*
		 * Send an email with the login details.
		 */
		ob_start();
		include_once(plugin_dir_path(__FILE__) . "../partials/emails/biobank-email-password-changed.php");
		$body = ob_get_contents();
		ob_end_clean();

		$sent = wp_mail(
			$email, "[Dwarna] Password Changed",
			$body, array( "Content-type: text/html" )
		);
		return true;
	}

	/**
	 * Get the blockchain solution's access token.
	 * It is assumed that this access token is stored in a cookie.
	 *
	 * @return	string	The blockchain access token.
	 */
	public function get_blockchain_access_token() {
		require(plugin_dir_path(__FILE__) . "../includes/globals.php");
		$access_token = $_COOKIE[BLOCKCHAIN_ACCESS_TOKEN];
		// A Hyperledger Composer access token looks like this:
		// s:05xpfhY0HIrDzs53FeqgYJ47oP5swGnZLsvHD2aWAwN52trpfPCEViJaTcSQ9LfC.Q1kYwi0cRB9T47G/fN0RzDXyLoh0hb1XDqnKMkkh40A
		$access_token = substr($access_token, 2, strpos($access_token, '.') - 2);
		return $access_token;
	}

	/**
	 * Change the login logo to Dwarna's.
	 */
	function change_login_logo() {
		echo '<style type="text/css">
			h1 a {
				background-image: url(' . get_site_url() . '/wp-content/plugins/biobank-plugin/assets/dwarna-logo.png) !important;
				background-size: cover !important;
				height: 70px !important;
				width: 68% !important;
			}
		</style>';
	}

	/**
	 * Get the slug of the current post or page.
	 *
	 * The function constructs the URL without the query.
	 * Then, it removes the home URL, thus leaving only the slug.
	 *
	 * @since 1.0.0
	 * @access private
	 *
	 * @return	string	The slug of the current post or page.
	 */
	private function get_current_slug() {
		if (isset($_SERVER["REDIRECT_URL"])) {
			$url = $_SERVER["REQUEST_SCHEME"] . "://" . $_SERVER["SERVER_NAME"] . $_SERVER["REDIRECT_URL"];
			return substr($url, strlen(home_url()) + 1, -1);
		} else {
			return;
		}
	}

}
