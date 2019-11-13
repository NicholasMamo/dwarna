<?php

/**
 * The file that handles form submissions.
 * The functions in this class are used to help process user form submissions.
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
 * The form handler class used to manage participant inputs from forms.
 *
 * This class validates and sanitizes inputs from various forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class ParticipantFormHandler extends UserFormHandler {

	/**
	 * Validate the given participant and try to add them to the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function create_participant() {
		$error = "";
		$endpoint = "participant"; // the REST API's endpoint

		if(isset($_POST["participant_nonce"]) && wp_verify_nonce($_POST["participant_nonce"], "participant_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create participants
			 */
			if (current_user_can("biobank_create_participant") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);
				$valid_email = $this->validate_email($input["email"]);
				$valid_password = $this->validate_password($input["password"]);
				$valid_new_user = $this->validate_new_user($input["username"], $input["email"]);

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
					$valid_email,
					$valid_password,
					$valid_new_user
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("username", $input["username"]);
					$request->add_parameter("password", $input["password"]);
					$request->add_parameter("email", $input["email"]);
					$request->add_parameter("first_name", $input["first_name"]);
					$request->add_parameter("last_name", $input["last_name"]);
					$response = $request->send_post_request($endpoint);

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";

						if (empty($error)) {
							$user_data = array(
							    "user_login" => $input["username"],
								"user_email" => $input["email"],
							    "user_pass" => $input["password"],
								"role" => "participant"
							);

							$user_id = wp_insert_user($user_data);
							/*
							 * Hash the email address to use it as a reverse index.
							 */
							update_user_meta($user_id, 'hashed_email', hash('sha256', $input['email']));
							$error = is_wp_error($user_id) ? "WordPress could not create the participant" : "";
						}
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
		wp_redirect(admin_url("admin.php") . "?page=biobank_partners&error=$error&redirect=create");
		exit;
	}

	/**
	 * Validate the given participant and try to update their data.
	 *
	 * @since	1.0.0
	 */
	public function update_participant() {
		$error = "";
		$endpoint = "participant"; // the REST API's endpoint
		$return = "";

		if(isset($_POST["participant_nonce"]) && wp_verify_nonce($_POST["participant_nonce"], "participant_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create participants
			 */
			if (current_user_can("biobank_create_participant") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];
				$user = get_user_by("login", $input["username"]); // fetch the user
				$return = $input["username"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);
				$valid_email = $this->validate_email($input["email"], $user->data->user_email);

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
					$valid_email
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("username", $input["username"]);
					$request->add_parameter("password", $input["password"]);
					$request->add_parameter("email", $input["email"]);
					$request->add_parameter("first_name", $input["first_name"]);
					$request->add_parameter("last_name", $input["last_name"]);
					$response = $request->send_post_request($endpoint, $method='PUT');

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";

						if (empty($error)) {
							/*
							 * Get the user's ID since this is an update operation.
							 * Then, include this ID in the user data.
							 */
							$id = get_user_by("login", $input["username"])->data->ID;
							$user_data = array(
								"ID" => "$id",
								"user_login" => $input["username"],
								"user_email" => $input["email"]
							);

							/*
							 * Only update the password if it is not empty
							 */
							if ($input["password"] != "") {
								$user_data["user_pass"] = wp_hash_password($input["password"]);
							}

							$user_id = wp_insert_user($user_data);
							/*
							 * Hash the email address to use it as a reverse index.
							 */
							update_user_meta($user_id, 'hashed_email', hash('sha256', $input['email']));
							$error = is_wp_error($user_id) ? "WordPress could not update the participant" : ""; // this error could be due to duplicate usernames or emails
						}
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
		wp_redirect(admin_url("admin.php") . "?page=biobank_partners&error=$error&action=update&redirect=update" . (empty($return) ? "" : "&username=$return"));
	}

	/**
	 * Validate the given participant and try to remove them from the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function remove_participant() {
		$error = "";
		$endpoint = "participant"; // the REST API's endpoint

		if(isset($_POST["participant_nonce"]) && wp_verify_nonce($_POST["participant_nonce"], "participant_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create participants
			 */
			if (current_user_can("biobank_create_participant") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("username", $input["username"]);

					/*
					 * Process the response
					 */
					$response = $request->send_post_request($endpoint, "DELETE");
					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";

						if (empty($error)) {
							$id = get_user_by("login", $input["username"])->data->ID;

							$status = wp_delete_user($id);
							$error = $status ? "" : "WordPress could not delete the participant";
						}
					} else {
						/*
						 * If a connection could not be established
						 */
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_partners&error=$error&redirect=remove");

	}

	/**
	 * Check whether the currently-logged in user has a temporary card.
	 *
	 * @since	1.0.0
	 * @param	boolean		$temp		A boolean that indicates whether the card is temporary or credentials-ready.
	 * @param	int			$study_id	The ID of the study related to the card will be checked.
	 *
	 * @return	stdClass	A class that contains the returned boolean in the `data` property.
	 */
	public function has_card($temp, $study_id) {
		$error = "";
		$endpoint = "has_card"; // the REST API's endpoint

		/*
		 * For security purposes, ensure that the user can update their consent.
		 * If they can update consent, they have a card that they can access.
		 */
		if (current_user_can("biobank_update_consent")) {
			/*
			 * Create a request and fetch the response
			 */
			$user = wp_get_current_user();
			$request = new \client\Request($this->scheme, $this->host, $this->port);
			$request->add_parameter("username", $user->user_login);
			$request->add_parameter("temp", $temp);
			$request->add_parameter("study_id", $study_id);

			/*
			 * Process the response
			 */
			$response = $request->send_get_request($endpoint);
			if (! is_wp_error($response)) {
				$body = json_decode($response["body"]);
				$error = isset($body->error) ? $body->error : "";
				return $body;
			} else {
				/*
				 * If a connection could not be established
				 */
				$body = new \stdClass();
				$body->error = "WordPress could not reach the backend";
			}
		}
		return $body;
	}

	/**
	 * Get the currently logged-in user's temporary card.
	 *
	 * @since	1.0.0
	 * @param	boolean		$temp		A boolean that indicates whether the card is temporary or credentials-ready.
	 * @param	int			$study_id	The ID of the study related to the card will be checked.
	 *
	 * @return	stdClass	A class that contains the returned card in the `data` property.
	 */
	public function get_card($temp, $study_id) {
		$error = "";
		$endpoint = "get_card"; // the REST API's endpoint

		/*
		 * For security purposes, ensure that the user can update their consent.
		 * If they can update consent, they have a card that they can access.
		 */
		if (current_user_can("biobank_update_consent")) {
			/*
			 * Create a request and fetch the response
			 */
			$user = wp_get_current_user();
			$request = new \client\Request($this->scheme, $this->host, $this->port);
			$request->add_parameter("username", $user->user_login);
			$request->add_parameter("temp", $temp);
			$request->add_parameter("study_id", $study_id);

			/*
			 * Process the response
			 */
			$response = $request->send_get_request($endpoint);
			if (! is_wp_error($response)) {
				$body = new \stdClass();
				$body->data = $response["body"];
				$error = isset($body->error) ? $body->error : "";
				return $body;
			} else {
				/*
				 * If a connection could not be established
				 */
				$body = new \stdClass();
				$body->error = "WordPress could not reach the backend";
			}
		}
		return $body;
	}

	/**
	 * Save the currently logged-in user's credentials-ready card.
	 *
	 * @since	1.0.0
	 * @param	string		$card		The card data to save.
	 * @param	string		$address	The participant's address on the blockchain.
	 *
	 * @return	stdClass	A class that contains the returned card in the `data` property.
	 */
	public function save_card($card, $address) {
		$error = "";
		$endpoint = "save_cred_card"; // the REST API's endpoint

		/*
		 * For security purposes, ensure that the user can update their consent.
		 * If they can update consent, they have a card that they can access.
		 */
		if (current_user_can("biobank_update_consent")) {
			/*
			 * Create a request and fetch the response
			 */
			$user = wp_get_current_user();

			$request = new \client\Request($this->scheme, $this->host, $this->port);
			$headers = array(
				"Content-Type: multipart/form-data",
				"Authorization: " . $request->get_token()
			); // cURL headers for file uploading
			$postfields = array("card" => "@$card", "username" => $user->user_login, "address" => $address);
			$ch = curl_init();
			$options = array(
				CURLOPT_URL => $this->scheme . "://" . $this->host . ":" . $this->port . "/$endpoint",
				CURLOPT_HEADER => true,
				CURLOPT_POST => 1,
				CURLOPT_HTTPHEADER => $headers,
				CURLOPT_POSTFIELDS => $postfields,
				CURLOPT_RETURNTRANSFER => true
			); // cURL options
			curl_setopt_array($ch, $options);
			curl_exec($ch);

			if(!curl_errno($ch)) {
				$info = curl_getinfo($ch);
			}

			$body = new \stdClass();
			if (isset($info) && $info['http_code'] == 200) {
				$body->data = true;
				$body->error = "";
			} else {
				$body->data = false;
				$body->error = curl_error($ch);
			}
			curl_close($ch);
		}
		return $body;
	}



	/**
	 * Get the given participant from the backend.
	 *
	 * @param	string	$username	The username of the research partner to retrieve.
	 *
	 * @since	1.0.0
	 */
	public function get_participant($username) {
		$error = "";
		$endpoint = "participant"; // the REST API's endpoint

		/*
		 * For security purposes, ensure that the user can indeed edit research partners.
		 */
		if (current_user_can("biobank_edit_participant")) {
			/*
			 * Create a request and fetch the response
			 */
			$request = new \client\Request($this->scheme, $this->host, $this->port);
			$request->add_parameter("username", $username);
			$response = $request->send_get_request($endpoint);

			if (! is_wp_error($response)) {
				$body = json_decode($response["body"]);
				$body->data = $body->data[0];
				return $body;
			} else {
				/*
				 * If no response is received, then a connection with the backend could not be established
				 */
				return (object) [ 'error' => "WordPress could not reach the backend" ];
			}
		}
	}

}

/**
 * The form handler class used to manage researcher inputs from forms.
 *
 * This class validates and sanitizes inputs from various forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class ResearcherFormHandler extends UserFormHandler {

	/**
	 * Validate the given researcher and try to add them to the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function create_researcher() {
		$error = "";
		$endpoint = "researcher"; // the REST API's endpoint

		if(isset($_POST["researcher_nonce"]) && wp_verify_nonce($_POST["researcher_nonce"], "researcher_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create researchers
			 */
			if (current_user_can("biobank_create_researcher") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);
				$valid_email = $this->validate_email($input["email"]);
				$valid_first_name = $this->validate_required_string($input["first_name"], "First name cannot be empty");
				$valid_last_name = $this->validate_required_string($input["last_name"], "Last name cannot be empty");
				$valid_password = $this->validate_password($input["password"]);
				$valid_new_user = $this->validate_new_user($input["username"], $input["email"]);

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
					$valid_email,
					$valid_first_name,
					$valid_last_name,
					$valid_password,
					$valid_new_user
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("username", $input["username"]);

					/*
					 * Process the response
					 */
					$response = $request->send_post_request($endpoint);

					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";

						if (empty($error)) {
							$user_data = array(
							    "user_login" => $input["username"],
								"user_email" => $input["email"],
							    "user_pass" => $input["password"],
								"first_name" => $input["first_name"],
								"last_name" => $input["last_name"],
								"role" => "researcher"
							);

							$user_id = wp_insert_user($user_data);
							update_user_meta($user_id, "affiliation", $input["affiliation"]);
							update_user_meta($user_id, "role", $input["role"]);
							$error = is_wp_error($user_id) ? "WordPress could not create the researcher" : ""; // this error could be due to duplicate usernames or emails
						}
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
		wp_redirect(admin_url("admin.php") . "?page=biobank_researchers&error=$error&redirect=create");

	}

	/**
	 * Validate the given researcher and try to update their data.
	 *
	 * @since	1.0.0
	 */
	public function update_researcher() {
		$error = "";
		$return = "";

		if(isset($_POST["researcher_nonce"]) && wp_verify_nonce($_POST["researcher_nonce"], "researcher_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create researchers
			 */
			if (current_user_can("biobank_create_researcher") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];
				$user = get_user_by("login", $input["username"]); // fetch the user
				$return = $input["username"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);
				$valid_email = $this->validate_email($input["email"], $user->data->user_email);
				$valid_first_name = $this->validate_required_string($input["first_name"], "First name cannot be empty");
				$valid_last_name = $this->validate_required_string($input["last_name"], "Last name cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
					$valid_email,
					$valid_first_name,
					$valid_last_name
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Get the user's ID since this is an update operation.
					 * Then, include this ID in the user data.
					 */
					$id = get_user_by("login", $input["username"])->data->ID;
					$user_data = array(
						"ID" => "$id",
						"user_login" => $input["username"],
						"user_email" => $input["email"],
						"user_pass" => $input["password"],
						"first_name" => $input["first_name"],
						"last_name" => $input["last_name"],
						"display_name" => sprintf("%s %s", $input["first_name"], $input["last_name"]),
					);

					/*
					 * Only update the password if it is not empty.
					 */
					if ($input["password"] != "") {
						$user_data["user_pass"] = wp_hash_password($input["password"]);
					}

					$user_id = wp_insert_user($user_data);
					update_user_meta($user_id, "affiliation", $input["affiliation"]);
					update_user_meta($user_id, "role", $input["role"]);
					$error = is_wp_error($user_id) ? "WordPress could not update the researcher" : ""; // this error could be due to duplicate usernames or emails
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_researchers&error=$error&action=update&redirect=update" . (empty($return) ? "" : "&username=$return"));
	}

	/**
	 * Validate the given researcher and try to remove them from the biobank's backend.
	 *
	 * @since	1.0.0
	 */
	public function remove_researcher() {
		$error = "";
		$endpoint = "researcher"; // the REST API's endpoint

		if(isset($_POST["researcher_nonce"]) && wp_verify_nonce($_POST["researcher_nonce"], "researcher_form")) {
			/*
			 * For security purposes, ensure that the user can indeed create researchers
			 */
			if (current_user_can("biobank_create_researcher") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_username = $this->validate_username($input["username"]);

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_username,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("username", $input["username"]);

					/*
					 * Process the response
					 */
					$response = $request->send_post_request($endpoint, "DELETE");
					if (! is_wp_error($response)) {
						$body = json_decode($response["body"]);
						$error = isset($body->error) ? $body->error : "";

						if (empty($error)) {
							$id = get_user_by("login", $input["username"])->data->ID;

							$status = wp_delete_user($id);
							$error = $status ? "" : "WordPress could not delete the researcher";
						}
					} else {
						/*
						 * If a connection could not be established
						 */
						$error = "WordPress could not reach the backend";
					}
				}
			}
		}
		$error = urlencode($error);
		wp_redirect(admin_url("admin.php") . "?page=biobank_researchers&error=$error&redirect=remove");

	}

}

?>
