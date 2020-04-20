<?php

/**
 * The file that handles form submissions.
 * The functions in this class are used to help process study form submissions.
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
class StudyFormHandler extends StudyHandler {

	/**
	 * Get information about a single study.
	 *
	 * Fetch all information about a study.
	 * Any errors are also stored in the returned array.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	int		$study_id The unique ID of the study.
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_study($study_id) {
		$endpoint = "study";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("study_id", $study_id);

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
	 * Get a list of participants in a particular study.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	int		$study_id The unique ID of the study.
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_participants_by_study($study_id) {
		$endpoint = "get_participants_by_study";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("study_id", $study_id);

		$response = $request->send_get_request($endpoint);
		if (! is_wp_error($response)) {
			$body = (object) json_decode($response["body"]);
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
	 * Search for studies.
	 *
	 * Look for studies in the backend.
	 * Any errors are also stored in the returned array.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	int		$number The number of search results to fetch.
	 * @param	int		$page The page number from where to resume the search.
	 * @param	string	$search The search string to use.
	 * @return	array 	The array containing the parsed response.
	 */
	public function search_studies($number, $page, $search) {
		$endpoint = "get_studies";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("number", $number);
		$request->add_parameter("page", $page);
		$request->add_parameter("search", $search);

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
	 * Search for studies that belong to the given researcher.
	 *
	 * Look for studies that belong to the given researcher in the backend.
	 * Any errors are also stored in the returned array.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string	$researcher The name of the researcher whose studies will be searched.
	 * @param	int		$number The number of search results to fetch.
	 * @param	int		$page The page number from where to resume the search.
	 * @param	string	$search The search string to use.
	 * @return	array 	The array containing the parsed response.
	 */
	public function search_researcher_studies($researcher, $number, $page, $search) {
		$endpoint = "get_studies_by_researcher";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("researcher", $researcher);
		$request->add_parameter("number", $number);
		$request->add_parameter("page", $page);
		$request->add_parameter("search", $search);

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
	 * Validate the given study and try to add them to the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function create_study() {
		$error = "";
		$endpoint = "study"; // the REST API's endpoint

		if(isset($_POST["study_nonce"]) && wp_verify_nonce($_POST["study_nonce"], "study_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create studies
			 */
			if (current_user_can("biobank_create_study") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];
				$researchers = isset($input["chosen_researchers"]) ? array_keys($input["chosen_researchers"]) : array();

				/*
				 * Perform validation
				 */
				$valid_id = $this->validate_required_string($input["study_id"], "The study ID cannot be empty");
				$valid_name = $this->validate_required_string($input["name"], "The study name cannot be empty");
				$valid_description = $this->validate_required_string($input["description"], "The study description cannot be empty");
				$valid_homepage = $this->validate_required_string($input["homepage"], "The study homepage cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_id,
					$valid_name,
					$valid_description,
					$valid_homepage,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Sanitize the study.
					 */
					$input = $this->sanitize_study($input);

					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("study_id", $input["study_id"]);
					$request->add_parameter("name", $input["name"]);
					$request->add_parameter("description", $input["description"]);
					$request->add_parameter("homepage", $input["homepage"]);
					$request->add_parameter("researchers", $researchers);
					$response = $request->send_post_request($endpoint);

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";
					} else {
						/*
						 * If no response is received, then a connection with the backend could not be established
						 */
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_studies&biobank_error=$error&redirect=create");

	}

	/**
	 * Validate the given study and try to update it in the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function update_study() {
		$error = "";
		$endpoint = "study"; // the REST API's endpoint
		$return = "";

		if(isset($_POST["study_nonce"]) && wp_verify_nonce($_POST["study_nonce"], "study_form")) {
			/*
			 * For security purposes, ensure that the user can indeed update studies
			 */
			if (current_user_can("biobank_edit_study") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];
				$researchers = isset($input["chosen_researchers"]) ? array_keys($input["chosen_researchers"]) : array();
				$return = $input["study_id"];
				if ($_FILES['attachment']) {
					$attachment = wp_handle_upload($_FILES['attachment'], Array('action' => 'update_study'));
					$error = isset($attachment['error']) ? $attachment['error'] : $error;
					$url = $attachment['url'];
				}

				/*
				 * Perform validation
				 */
				$valid_id = $this->validate_required_string($input["study_id"], "The study ID cannot be empty");
				$valid_name = $this->validate_required_string($input["name"], "The study name cannot be empty");
				$valid_description = $this->validate_required_string($input["description"], "The study description cannot be empty");
				$valid_homepage = $this->validate_required_string($input["homepage"], "The study homepage cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_id,
					$valid_name,
					$valid_description,
					$valid_homepage,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Sanitize the study.
					 */
					$input = $this->sanitize_study($input);

					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("study_id", $input["study_id"]);
					$request->add_parameter("name", $input["name"]);
					$request->add_parameter("description", $input["description"]);
					$request->add_parameter("homepage", $input["homepage"]);
					if (isset($url)) {
						$request->add_parameter("attachment", $url);
					}
					$request->add_parameter("researchers", $researchers);
					$response = $request->send_post_request($endpoint, "PUT");

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";
					} else {
						/*
						 * If no response is received, then a connection with the backend could not be established
						 */
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_studies&biobank_error=$error&action=update&redirect=update" . (empty($return) ? "" : "&study_id=$return"));

	}

	/**
	 * Delete the given study from the biobank backend.
	 *
	 * @since	1.0.0
	 */
	public function remove_study() {
		$error = "";
		$endpoint = "study"; // the REST API's endpoint

		if(isset($_POST["study_nonce"]) && wp_verify_nonce($_POST["study_nonce"], "study_form")) {
			/*
			 * For security purposes, ensure that the user can indeed remove studies
			 */
			if (current_user_can("biobank_remove_study") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_id = $this->validate_required_string($input["study_id"], "The study ID cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_id,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("study_id", $input["study_id"]);
					$response = $request->send_post_request($endpoint, "DELETE");

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";
					} else {
						/*
						 * If no response is received, then a connection with the backend could not be established
						 */
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_studies&biobank_error=$error&redirect=remove");

	}

	/**
	 * Sanitize the study.
	 *
	 * @since	1.0.0
	 * @access	private
	 * @param	array	$study The study input array.
	 * @return	array	The array containing the sanitized study.
	 */
	private function sanitize_study($study) {
		/*
		 * If the study homepage does not start with a protocol, add it.
		 */
		if (! preg_match('/https?:\/\//', $study['homepage'])) {
			$study['homepage'] = "https://{$study['homepage']}";
		}
		$study['name'] = stripcslashes($study['name']);
		$study['description'] = stripcslashes($study['description']);

		return $study;
	}

}

?>
