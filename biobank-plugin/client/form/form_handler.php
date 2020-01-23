<?php

/**
 * The file that handles form submissions.
 *
 * The functions in this class are used to help process form submissions.
 * This process includes validating and sanitizing data before sending any requests.
 * The general workflow is as follows:
 *
 *	1. Ensure that the request is legit.
 * 	2. Ensure that the logged-in user has the necessary permissions to make the request.
 * 	3. If form input is provided and needed, fetch it.
 * 	4. If input is provided, validate it.
 * 	5. If input is provided, sanitize it.
 * 	6. If communication with the backend is required, create and send a request to the REST API.
 * 	7. If the response is valid, update the frontend as well.
 * 	8. Redirect to the next page, including any errors in the query string.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/client/forms
 */

namespace client\form;
use \DateTime;

require_once( ABSPATH . 'wp-admin/includes/plugin.php' );

require_once(plugin_dir_path(__FILE__) . "validation/status.php");

/**
 * The abstract form handler class used to manage inputs from forms.
 *
 * This class validates and sanitizes inputs from various forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
abstract class FormHandler {

	/**
	 * The scheme used to connect to the REST API.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		string		The scheme used to connect to the REST API.
	 */
	protected $scheme;

	/**
	 * The hostname where the REST API resides.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		string		The hostname where the REST API resides.
	 */
	protected $host;

	/**
	 * The port used to connect to the REST API.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		int			The port used to connect to the REST API.
	 */
	protected $port;

	/**
	 * Create the form handler with information about the REST API.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string		$scheme		The scheme used to connect to the REST API.
	 * @param	string		$host		The hostname where the REST API resides.
	 * @param	int			$port		The port used to connect to the REST API.
	 */
	public function __construct($scheme=NULL, $host=NULL, $port=NULL) {
		$options = get_option("biobank");

		$this->scheme = is_null($scheme) ? $options["scheme"] : $scheme;
		$this->host = is_null($host) ? $options["host"] : $host;
		$this->port = is_null($port) ? $options["port"] : $port;
	}

	/**
	 * Ping the server to check whether the connection is established.
	 *
	 * @since 1.0.0
	 * @access	public
	 * @return	bool	A boolean indicating whether the ping was successful
	 */
	public function ping() {
		$request = new \client\Request($this->scheme, $this->host, $this->port);
		$response = $request->send_get_request("ping");
		return ! is_wp_error($response) && $response["response"]["code"] == 200;
	}

	/**
	 * Get the blockchain solution's access token.
	 * It is assumed that this access token is stored in a cookie.
	 */
	public function get_blockchain_access_token() {
		require(plugin_dir_path(__FILE__) . "../../includes/globals.php");
		$access_token = $_COOKIE[$blockchain_access_token];
		// A Hyperledger Composer access token looks like this:
		// s:05xpfhY0HIrDzs53FeqgYJ47oP5swGnZLsvHD2aWAwN52trpfPCEViJaTcSQ9LfC.Q1kYwi0cRB9T47G/fN0RzDXyLoh0hb1XDqnKMkkh40A
		$access_token = substr($access_token, 2, strpos($access_token, '.') - 2);
		return $access_token;
	}

	/**
	 * Validation
	 */

	/**
	 * Validate the value of a general, required field.
	 *
	 * Required fields cannot be empty.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$string		The string to validate
	 * @param	string	$message	The message to display
	 * @return	Status	A status object
	 */
	protected function validate_required_string($string, $message) {
		/*
		 * A required string cannot be empty
		 */
		if (empty($string)) {
			return new Status(false, $message);
		}
		return new Status(true);
	}

	/**
	 * Validate the given email.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$email		The email to validate
	 * @return	Status	A status object
	 */
	protected function validate_email($email) {
		$filter = is_array($filter) ? $filter : array($filter); // make the filter a list if it is not one already.

		/*
		 * An email address cannot be empty
		 */
		if (empty($email)) {
			return new Status(false, "Email cannot be empty");
		}

		/*
		 * Check the email address' syntax
		 */
		if (! is_email($email)) {
			return new Status(false, "Invalid email address");
		}

		return new Status(true);
	}

	/**
	 * Iterate over the given statuses to ensure that they are all successful.
	 *
	 * If an unsuccessful status is found, return it and exit.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	array	$statuses	A list of statuses to validate
	 * @return	Status	The first unsuccessful status instance, or a new successful status instance if everything is fine
	 */
	protected function validate($statuses) {
		$statuses = is_array($statuses) ? $statuses : array($statuses); // convert a single status into an array
		foreach($statuses as $status) {
			if (!$status->is_successful()) {
				return $status;
			}
		}
		return new Status();
	}

	/**
	 * Sanitization
	 */

	 /**
 	 * Convert the given date into ISO 8601 format - YYYY-MM-DD
	 *
	 * It is assumed that the date is initially in the form DD-MM-YYYY.
 	 *
 	 * @since	1.0.0
 	 * @access	protected
 	 * @param	string	$date		The date to format.
 	 * @return	string	The new date, formatted in ISO 8061 format.
 	 */
 	protected function format_date($date) {
 		return DateTime::createFromFormat("d-m-Y", $date)->format("Y-m-d");
 	}

	/**
	* Convert the given date from ISO 8601 format - YYYY-MM-DD - to the form DD-MM-YYYY.
	*
	* It is assumed that the date is initially in the form YYYY-MM-DD.
	*
	* @since	1.0.0
	* @access	protected
	* @param	string	$date		The date to format in ISO 8601 standard.
	* @return	string	The new date, formatted normally.
	*/
   protected function date_from_iso($date) {
	   return DateTime::createFromFormat("Y-m-d", $date)->format("d-m-Y");
   }

}

/**
 * The form handler class used to manage general forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class GeneralFormHandler extends FormHandler { }

/**
 * The abstract form handler class used to manage user inputs from forms.
 *
 * This class validates and sanitizes inputs from various user forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
abstract class UserFormHandler extends FormHandler {

	/**
	 * Validate that the user does not exist.
	 * Most importantly, the username and email addresses are both unique.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$username	The username to check
	 * @param	string	$email		The email to validate
	 * @return	Status	A status object
	 */
	protected function validate_new_user($username, $email) {
		/*
		 * The username has to be unique
		 */
		if (get_user_by("login", $username)) {
			return new Status(false, "A user with that username already exists in WordPress");
		}

		/*
		 * The email address has to be unique
		 */
		if (get_user_by("email", $email)) {
			return new Status(false, "A user with that email address already exists in WordPress");
		}
		return new Status(true);
	}

	/**
	 * Validate the given username
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$username	The username to validate
	 * @return	Status	A status object
	 */
	protected function validate_username($username) {
		/*
		 * A username cannot be empty
		 */
		if (empty($username)) {
			return new Status(false, "Username cannot be empty");
		}
		return new Status(true);
	}

	/**
	 * Validate the given email.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$email		The email to validate
	 * @param	string	$filter		Permitted emails
	 * @return	Status	A status object
	 */
	protected function validate_email($email, $filter="") {
		$filter = is_array($filter) ? $filter : array($filter); // make the filter a list if it is not one already.

		/*
		 * An email address cannot be empty
		 */
		if (empty($email)) {
			return new Status(false, "Email cannot be empty");
		}

		/*
		 * Check the email address' syntax
		 */
		if (! is_email($email)) {
			return new Status(false, "Invalid email address");
		}

		/*
		 * Check that the email address is unique
		 */
		if (get_user_by("email", $email) && !in_array($email, $filter)) {
			return new Status(false, "A user with that email address already exists in WordPress");
		}

		return new Status(true);
	}

	/**
	 * Validate the given password
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	string	$password	The password to validate
	 * @return	Status	A status object
	 */
	protected function validate_password($password) {
		/*
		 * A password cannot be empty
		 */
		if (empty($password)) {
			return new Status(false, "Password cannot be empty");
		}
		return new Status(true);
	}

}

/**
 * The abstract form handler class used to manage study inputs.
 *
 * This class validates and sanitizes inputs from various study forms.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
abstract class StudyHandler extends FormHandler {

	/**
	 * Extract the attributes from the form submission.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @param	array	$parameters	The form parameters
	 * @return	array	An array of triplets - name, type, constraints - of the attributes
	 */
	protected function extract_attributes($parameters) {
		$attributes = isset($parameters["chosen_attributes"]) && isset($parameters["chosen_attributes"]["type"]) ? $parameters["chosen_attributes"] : array("name" => array());
		$triplets = array();

		/*
		 * Go through each attribute, collecting information about it.
		 */
		foreach ($attributes["name"] as $name) {
			$type = $attributes["type"][$name];
			$constraints = isset($attributes["option"][$name]) ? array_values($attributes["option"][$name]) : array();
			array_push($triplets, array($name, $type, $constraints));
		}
		return $triplets;
	}

}

?>
