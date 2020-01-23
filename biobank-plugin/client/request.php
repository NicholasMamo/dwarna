<?php

namespace client;

/*
 * Start the session. This is required because that is where the access token is stored.
 */
if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

/**
 * The file that defines a request that is made to the backend
 *
 * This class creates requests that are made to the REST API
 * It returns a request object as an array
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/client
 */

/**
 * The request class used to create most requests.
 *
 * This class is used to create requests that can be sent to the REST API.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class Request {

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
	 * The body of the request, including parameters.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		array 	$body		The request's body.
	 */
	protected $body = array();

	/**
	 * The headers of the request.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		array 	$headers	The request's headers.
	 */
	protected $headers = array();

	/**
	 * Create a request.
	 *
	 * Set any initial content that can be used further on by the class.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param		string		$scheme		The scheme used to connect to the REST API.
	 * @param		string		$host		The hostname where the REST API resides.
	 * @param		int			$port		The port used to connect to the REST API.
	 * @param		array 		$headers	The optional headers to include with the request.
	 * @param		array 		$body		The body parameters of the request.
	 */
	public function __construct($scheme, $host, $port, $body=array(), $headers=array()) {
		$this->body = $body;
		$this->headers = $headers;
		$this->scheme = $scheme;
		$this->host = $host;
		$this->port = $port;
	}

	/**
	 * Add a header to the request.
	 *
	 * Adds a new header to the associative array of the header.
	 * Overwrites the header if it already exists.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string	$name		The header's name.
	 * @param	mixed	$value		The header's new value.
	 */
	public function add_header($name, $value) {
		$this->headers[$name] = $value;
	}

	/**
	 * Add a parameter to the request's body.
	 *
	 * Adds a new parameter to the associative array of the body.
	 * Overwrites the parameter if it already exists.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string	$name		The parameter's name.
	 * @param	mixed	$value		The parameter's new value.
	 */
	public function add_parameter($name, $value) {
		$this->body[$name] = $value;
	}

	/**
	 * Add the parameters from the given array to the request's body.
	 *
	 * Adds each new parameter to the associative array of the body.
	 * Overwrites the parameter if it already exists.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	array	$parameters	An associative array
	 */
	public function add_parameters($parameters) {
		foreach($parameters as $name => $value) {
			$this->add_parameter($name, $value);
		}
	}

	/**
	 * Get the list of parameters in the request.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	array	The array containing a list of parameters.
	 */
	public function get_parameters() {
		return $this->body;
	}

	/**
	 * Construct the request.
	 *
	 * Uses the given headers and body to create a request.
	 * This request should also include the access token.
	 *
	 * @since	1.0.0
	 * @access	public
	 *
	 * @param	string		$method		The method to use.
	 *
	 * @return	array 		The array containing a list of headers and body parameters.
	 */
	public function create_request($method="POST") {
		if (!isset($this->headers["Content-type"])) {
			$this->add_header("Content-type", "application/json"); // add the content type; without it, the backend fails to read the request"s body
		}
		return array(
			"headers" => $this->headers,
			"body" => json_encode($this->body),
			"timeout" => 10,
			"method" => $method,
		);
	}

	/**
	 * Construct a GET request.
	 *
	 * Uses the given headers and body to create a request.
	 * This request should also include the access token.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	array 		The array containing a list of headers and URL parameters.
	 */
	public function create_get_request() {
		return array(
			"headers" => $this->headers
		);
	}

	/**
	 * Construct a URL to the REST API with the given endpoint.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string		$endpoint	The endpoint of the REST API.
	 * @param	string		$parameters	An associative array of key-value pairs.
	 * @return	string		The URL where the request should be made
	 */
	public function construct_url($endpoint, $parameters=array()) {
		$parameter_strings = array();
		foreach ($parameters as $key => $value) {
			if (gettype($value) == "boolean")  {
				/*
				 * If a boolean is provided, convert it into a string.
				 */
				$value = $value ? "true" : "false";

			}
			array_push($parameter_strings, "$key=$value");
		}
		$parameter_string = empty($parameters) ? "" : ("?" . implode("&", $parameter_strings));
		return sprintf("%s://%s:%d/%s%s", $this->scheme, $this->host, $this->port, $endpoint, $parameter_string);
	}

	/**
	 * Get the access token to be used for requests.
	 *
	 * If there is already an access token stored in the session variable, re-use it.
	 * Otherwise, ask for a new one.
	 * The function may also be forced to request a new token.
	 * This may be needed in case the token has expired.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	boolean		$force_new	A boolean that indicates whether an access token should be created forcibly.
	 * @return	string		The access token with the scopes associated with the user role.
	 */
	public function get_token($force_new=false) {
		/*
		 * Check if there is already an access token.
		 * If there isn't, request a new one.
		 * A new token should also be requested if forced.
		 */
	 	require(plugin_dir_path(__FILE__) . "/../includes/globals.php");
		if (!isset($_SESSION["Authorization"]) // if there is no token on record
			|| (isset($_SESSION["Authorization_Expiry"]) && $_SESSION["Authorization_Expiry"] < time()) // or the token has expired
			|| $force_new) { // or if the request was forced
			/*
			 * Only fetch a token if the user is logged in.
			 */
			if (\is_user_logged_in()) {
				$token_endpoint = get_option('biobank')['biobank-token-endpoint'];
				$url = $this->construct_url($token_endpoint); // create the URL in advance
				$user = wp_get_current_user();
				$role = $user->roles[0];
				$requested_scopes = $scopes[$role];

				/*
				 * Construct the request and send it.
				 */
				$body = array(
					"grant_type" => "client_credentials",
					"client_id" => $client_id,
					"client_secret" => $client_secret,
					"scope" => implode($requested_scopes, " "),
					"user_id" => $user->user_login
				);

				$response = wp_remote_post($url, array(
					"headers" => array(),
					"body" => $body,
				));

				/*
				 * The access token should be saved alongside the expiry timestamp.
				 * In this way, if the token is known to have expired, the request can be made right away.
				 * This avoids any prior failures and needless requests.
				 */
			 	if (! is_wp_error($response)) {
					$body = json_decode($response["body"]);
					$token = $body->access_token;
					$expiry = $body->expires_in;
					$_SESSION["Authorization"] = $token;
					$_SESSION["Authorization_Expiry"] = time() + $expiry;
					return $token;
				} else {
					return "";
				}
			}
		} else {
			return $_SESSION["Authorization"];
		}
		return "";
	}

	/**
	 * Send a POST request and return the response.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string		$endpoint	The endpoint of the REST API.
	 * @param	string		$method		The method to use.
	 *
	 * @return	array		The array containing the response.
	 */
	public function send_post_request($endpoint, $method="POST") {
		$url = $this->construct_url($endpoint); // create the URL in advance
		$token = $this->get_token();
		$this->add_header("Authorization", $token);
		$method = strtoupper($method);
		$response = wp_remote_request($url, $this->create_request($method));

		/*
		 * The response may fail because the token is invalid.
		 * One reason why this may happen is if it expired.
		 * In that case, force a token refresh and try again.
		 */
		if (! is_wp_error($response) && $response["response"]["code"] == 401) {
			$token = $this->get_token($force_new=true);
			$this->add_header("Authorization", $token);
			$response = wp_remote_request($url, $this->create_request($method));
		}
		return $response;
	}

	/**
	 * Send a GET request and return the response.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @param	string		$endpoint	The endpoint of the REST API.
	 * @return	array		The array containing the response.
	 */
	public function send_get_request($endpoint) {
		$url = $this->construct_url($endpoint, $this->get_parameters()); // create the URL in advance
		$token = $this->get_token();
		$this->add_header("Authorization", $token);
		$response = wp_remote_get($url, $this->create_get_request());

		/*
		 * The response may fail because the token is invalid.
		 * One reason why this may happen is if it expired.
		 * In that case, force a token refresh and try again.
		 */
		if (! is_wp_error($response) && $response["response"]["code"] == 401) {
			$token = $this->get_token($force_new=true);
			$this->add_header("Authorization", $token);
			$response = wp_remote_get($url, $this->create_get_request());
		}
		return $response;
	}

}
