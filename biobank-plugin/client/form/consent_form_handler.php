<?php

/**
 * The file that handles form submissions.
 * The functions in this class are used to help process consent form submissions.
 * They also handle data retrieval.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/client/forms
 */

namespace client\form;

require_once(plugin_dir_path(__FILE__) . "form_handler.php");

/**
 * The form handler class used to manage consent inputs from forms.
 *
 * This class validates and sanitizes inputs from various forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class ConsentFormHandler extends StudyHandler {

	/**
	 * Get a list of active studies.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_active_studies() {
		$endpoint = "get_active_studies";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$response = $request->send_get_request($endpoint);

		if (! is_wp_error($response)) {
			$body = json_decode($response["body"]);
			$body->error = isset($body->error) ? $body->error : "";
			return $body;
		} else {
			$body = new \stdClass();
			$body->data = array();
			$body->error = "WordPress could not reach the backend";
			return $body;
		}
	}

	/**
	 * Get a list of active studies that the user has consented to.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_studies_by_participant() {
		$endpoint = "get_studies_by_participant";

		$username = wp_get_current_user()->user_login;

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("username", $username);
		$request->add_parameter("access_token", $this->get_blockchain_access_token());
		$response = $request->send_get_request($endpoint);

		if (! is_wp_error($response)) {
			$body = json_decode($response["body"]);
			$body->error = isset($body->error) ? $body->error : "";
			return $body;
		} else {
			$body = new \stdClass();
			$body->data = array();
			$body->error = "WordPress could not reach the backend";
			return $body;
		}
	}

	/**
	 * Get a list of attribute values for the logged-in participant.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	array	$attributes	A list of unique attribute IDs whose values will be returrned.
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_participant_attributes($attributes) {
		$endpoint = "get_attributes";

		$username = wp_get_current_user()->user_login;

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("username", $username);
		$request->add_parameter("attributes", array_unique($attributes));
		$response = $request->send_post_request($endpoint);

		if (! is_wp_error($response)) {
			$body = json_decode($response["body"]);
			$body->error = isset($body->error) ? $body->error : "";
			return $body->data;
		} else {
			$body = new \stdClass();
			$body->data = array();
			$body->error = "WordPress could not reach the backend";
			return $body;
		}
	}

	/**
	 * Authenticate the user so that they consent to a study.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function authenticate() {
		error_log("In authenticate");
		$error = "";
		if(isset($_POST["consent_nonce"]) && wp_verify_nonce($_POST["consent_nonce"], "consent_form")) {
			/*
			 * For security purposes, ensure that the user can indeed update consent.
			 */
			if (current_user_can("biobank_update_consent") && isset($_POST["biobank"])) {
				/*
				 * If the user has the necessary permissions, save the consent data to the session.
				 */
				$input = $_POST["biobank"];
				$study = isset($input["study"]) ? $input["study"] : array();
				$_SESSION['study_id'] = $study['study_id'];

				/*
				 * Then, redirect them to authorization endpoint.
				 */
				wp_redirect(get_site_url() . "/index.php/biobank-study" . "?authorized=true&action=consent");
				exit;
			}
		}

		/*
		 * If something goes wrong, redirect back with an error.
		 */
		error_log("error in authenticate");
		require(plugin_dir_path(__FILE__) . "../../includes/globals.php");
		$error = urlencode($error);
		wp_redirect(get_site_url() . "/index.php/" . $plugin_pages['biobank-consent']['wp_info']['post_name'] . "?biobank_error=$error&return=" . __FUNCTION__);
		exit;
	}

	/**
	 * Set the consent and accompanying attributes for a user.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function update_consent() {
		$error = "";
		$input = $_POST["biobank"];
		$study = isset($input["study"]) ? $input["study"] : array();

		if(isset($_POST["consent_nonce"]) && wp_verify_nonce($_POST["consent_nonce"], "consent_form")) {
			/*
			 * For security purposes, ensure that the user can indeed update consent.
			 */
			if (current_user_can("biobank_update_consent") && isset($_POST["biobank"])) {
				$error = '';
				$give_endpoint = "give_consent";
				$withdraw_endpoint = "withdraw_consent";
				$consenting = isset($study['consenting']) && $study['consenting'] == 'on';
				
				error_log("Consenting");
				error_log($consenting);
				
				error_log("address");
				error_log($_SESSION['address']);
				/*
				 * Create a new request with the study and user information.
				 */
				$body = new \stdClass();
				$request = new \client\Request($this->scheme, $this->host, $this->port);
				$request->add_parameter("study_id", $study['study_id']);
				$request->add_parameter("address", $_SESSION['address']);
				$request->add_parameter("access_token", $this->get_blockchain_access_token());

				$consent = $consenting && $study['consent'] == 'on';
				/*
				 * There are two routes to consent.
				 * Either the participant gives it, or they withdraw it.
				 */
				if ($consent) {
					$response = $request->send_post_request($give_endpoint);
					if (! is_wp_error($response)) {
						$response_body = json_decode($response["body"]);
						print("Response from giving consent");
						error_log(print_r($response_body));
						$error = isset($response_body->error) ? $response_body->error : $error;
					} else {
						error_log("Found error when giving consent");
						$error = "WordPress could not reach the backend";
					}
				} else {
					$response = $request->send_post_request($withdraw_endpoint);
					if (! is_wp_error($response)) {
						$response_body = json_decode($response["body"]);
						print("Response from withdraw consent");
						error_log(print_r($response_body));
						$error = isset($response_body->error) ? $response_body->error : $error;
					} else {
						error_log("Found error when withdrawing consent");
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}

		require(plugin_dir_path(__FILE__) . "../../includes/globals.php");
		/*
		 * If something goes wrong, redirect back with an error.
		 */
		if (isset($study['study_id'])) {
			$error = urlencode($error);
			wp_redirect(get_site_url() . "/index.php/" . $plugin_pages['biobank-study']['wp_info']['post_name'] . "?action=consent&study={$study['study_id']}&biobank_error=$error&return=" . __FUNCTION__);
			exit;
		} else {
			$error = urlencode($error);
			wp_redirect(get_site_url() . "/index.php/" . $plugin_pages['biobank-consent']['wp_info']['post_name'] . "?biobank_error=$error&return=" . __FUNCTION__);
			exit;
		}
	}

	/**
	 * Save the consent and redirect back to the study.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function save_consent() {
		if (isset($_GET['authorized']) &&
			isset($_SESSION['study_id']) &&
			isset($_SESSION['consent'])
		) {
			$error = '';
			$give_endpoint = "give_consent";
			$withdraw_endpoint = "withdraw_consent";

			/*
			 * Create a new request with the study and user information.
			 */
			$body = new \stdClass();
			$request = new \client\Request($this->scheme, $this->host, $this->port);
			$request->add_parameter("study_id", $_SESSION['study_id']);
			$request->add_parameter("address", $_SESSION['address']);
			$request->add_parameter("access_token", $this->get_blockchain_access_token());
			$consent = $_SESSION['consent'];

			/*
			 * Unset the consumed session information.
			 */
			unset($_SESSION['study_id']);
			unset($_SESSION['consent']);

			/*
			 * There are two routes to consent.
			 * Either the participant gives it, or they withdraw it.
			 */
			if ($consent) {
				$response = $request->send_post_request($give_endpoint);
				if (! is_wp_error($response)) {
					$response_body = json_decode($response["body"]);
					$error = isset($response_body->error) ? $response_body->error : $error;
				} else {
					$error = "WordPress could not reach the backend";
				}
			} else {
				$response = $request->send_post_request($withdraw_endpoint);
				if (! is_wp_error($response)) {
					$response_body = json_decode($response["body"]);
					$error = isset($response_body->error) ? $response_body->error : $error;
				} else {
					$error = "WordPress could not reach the backend";
				}
			}
		}

		include(plugin_dir_path(__FILE__) . "../../includes/globals.php");
		wp_redirect(get_site_url() . "/index.php/{$plugin_pages['biobank-consent']['wp_info']['post_name']}");
		exit;
	}

	/**
	 * Get a participant's consent trail.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_consent_trail() {
		$endpoint = "get_consent_trail";

		$username = wp_get_current_user()->user_login;

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("username", $username);
		$request->add_parameter("access_token", $this->get_blockchain_access_token());
		$response = $request->send_get_request($endpoint);

		if (! is_wp_error($response)) {
			$body = json_decode($response["body"]);
			$body->error = isset($body->error) ? $body->error : "";
			return $body->data;
		} else {
			$body = new \stdClass();
			$body->data = array();
			$body->error = "WordPress could not reach the backend";
			return $body;
		}
	}

}

?>
