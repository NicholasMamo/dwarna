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
 * The form handler class used to manage study inputs from forms.
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
	 * Set the consent and accompanying attributes for a user.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function update_consent() {
		$error = "";
		$give_endpoint = "give_consent";
		$withdraw_endpoint = "withdraw_consent";

		if(isset($_POST["consent_nonce"]) && wp_verify_nonce($_POST["consent_nonce"], "consent_form")) {
			/*
			 * For security purposes, ensure that the user can indeed update studies
			 */
			if (current_user_can("update_consent") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];
				$studies = isset($input["study"]) ? $input["study"] : array();

				$body = new \stdClass();

				$username = wp_get_current_user()->user_login;

				/*
				 * Go through each study and update the consent.
				 */
				foreach ($studies as $study_id => $study_data) {
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("study_id", $study_id);
					$request->add_parameter("username", $username);
					$request->add_parameter("access_token", $this->get_blockchain_access_token());

					/*
					 * There are two routes to consent.
					 * Either the participant gives it, or they withdraw it.
					 */
					if (isset($study_data["consent"]) && $study_data["consent"] == "on") {
						$request->add_parameter("attributes", $study_data["attributes"]);
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

			}
		}

		$error = urlencode($error);
		wp_redirect(get_site_url() . "/index.php/biobank-consent?error=$error&return=" . __FUNCTION__);
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
