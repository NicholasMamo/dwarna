<?php

/**
 * The file that handles email form submissions.
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
class EmailFormHandler extends FormHandler {

	/**
	 * Create a new email.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function create_email() {
		$error = "";
		$endpoint = "email"; // the REST API's endpoint

		if(isset($_POST["email_nonce"]) && wp_verify_nonce($_POST["email_nonce"], "email_form")) {
			/*
			 * For security purposes, ensure that the user can indeed send emails
			 */
			if (current_user_can("biobank_send_email") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_subject = $this->validate_required_string($input["subject"], "The subject cannot be empty");
				$valid_body = $this->validate_required_string($input["body"], "The body cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_subject,
					$valid_body,
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					/*
					 * Create a request and fetch the response
					 */
					$request = new \client\Request($this->scheme, $this->host, $this->port);
					$request->add_parameter("subject", $input["subject"]);
					$request->add_parameter("body", $input["body"]);
					$request->add_parameter("recipient_group", $input["recipient-group"]);
					$request->add_parameter("recipients", $input["recipient"]);
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
		wp_redirect(admin_url("admin.php") . "?page=biobank_emails&error=$error&redirect=create");
		exit;
	}

	/**
	 * Remove an email.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function remove_email() {
		$error = "";
		$endpoint = "email"; // the REST API's endpoint

		if(isset($_POST["email_nonce"]) && wp_verify_nonce($_POST["email_nonce"], "email_form")) {
			/*
			 * For security purposes, ensure that the user can indeed send emails
			 */
			if (current_user_can("biobank_remove_email") && isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Perform validation
				 */
				$valid_id = $this->validate_required_string($input["email_id"], "The email ID cannot be empty");

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
					$request->add_parameter("id", $input["email_id"]);
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
		wp_redirect(admin_url("admin.php") . "?page=biobank_emails&error=$error&redirect=remove");
		exit;
	}

	/**
	 * Update the subscription to receive biobank-related emails.
	 * The function expects a research partner username.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function update_subscription() {
		$error = "";
		$endpoint = "subscription"; // the REST API's endpoint

		if(isset($_POST["subscription_nonce"]) && wp_verify_nonce($_POST["subscription_nonce"], "subscription_form")) {
			if (isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Create a request and fetch the response
				 */
				$request = new \client\Request($this->scheme, $this->host, $this->port);
				$request->add_parameter("username", wp_get_current_user()->user_login);
				$request->add_parameter("subscription", 'any_email');
				$request->add_parameter("subscribed", $input['any_email'] == 'on');
				$response = $request->send_post_request($endpoint, "POST");

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
		$error = urlencode($error);

		require(plugin_dir_path(__FILE__) . "../../includes/globals.php");
		wp_redirect(home_url($plugin_pages['biobank-subscription']['wp_info']['post_name']) . "?redirect=update&error=$error");
		exit;
	}

	/**
	 * Forward the recruitment form to the biobank.
	 *
	 * @since	1.0.0
	 * @access	public
	 */
	public function forward_recruitment() {
		$error = "";
		$endpoint = "subscription"; // the REST API's endpoint
		require(plugin_dir_path(__FILE__) . "../../includes/globals.php");

		if(isset($_POST["recruitment_nonce"]) && wp_verify_nonce($_POST["recruitment_nonce"], "recruitment_form")) {
			if (isset($_POST["biobank"])) {
				$input = $_POST["biobank"];

				/*
				 * Verify that all the required details were provided and are correct.
				 */
				$valid_id = $this->validate_required_string($input["name"], "The name cannot be empty");
				$valid_email = $this->validate_email($input["email"]);
				$valid_mobile = $this->validate_required_string($input["mobile"], "The mobile number cannot be empty");

				/*
				 * Ensure that everything checks out
				 */
				$validation_check = $this->validate(array(
					$valid_id,
					$valid_email,
					$valid_mobile
				));

				if (! $validation_check->is_successful()) {
					$error = (string) $validation_check;
				} else {
					$sent = wp_mail(
						'nicholas.mamo@um.edu.mt',
						"New Research Partner: {$input['name']}",
						"<p>New Research Partner: {$input['name']}</p>
						 <p>Mobile: {$input['mobile']}</p>
						 <p>Email: {$input['email']}</p>",
						 array(
							 "Content-type: text/html"
						 )
					);

					if (! $sent) {
						$error = "Email could not be sent";
					}
				}
			}
		}
		$error = urlencode($error);

		wp_redirect(home_url($plugin_pages['biobank-recruitment']['wp_info']['post_name']) . "?redirect=update&error=$error");
		exit;
	}

	/**
	 * Get a single email.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	int		$number The number of search results to fetch.
	 * @param	int		$page The page number from where to resume the search.
	 * @param	string	$search The search string to use.
	 * @return	array 	The array containing the parsed response.
	 */
	public function search_emails($number, $page, $search) {
		$endpoint = "email";

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
	 * Get the user's subscriptions.
	 *
	 * @since	1.0.0
	 * @access	public
	 *
	 * @param	string	$username	The username of the user whose subscriptions will be fetched.
	 *								If no username is given, the currently logged-in user's subscriptions are fetched.
	 *
	 * @return	array	The list of user subscriptions.
	 */
	public function get_subscriptions($username=null) {
		$error = "";
		$endpoint = "subscription"; // the REST API's endpoint

		/*
		 * Create a request and fetch the response
		 */
		$request = new \client\Request($this->scheme, $this->host, $this->port);

		$username  = $username ?? wp_get_current_user()->user_login;
		$request->add_parameter("username", $username);

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
	 * Search for emails.
	 *
	 * Look for emails in the backend.
	 * Any errors are also stored in the returned array.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	int		$id The ID of the email to fetch.
	 * @return	array 	The array containing the parsed response.
	 */
	public function get_email($id) {
		$endpoint = "email";

		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$request->add_parameter("id", $id);

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

}
