<?php

/**
 * Statuses are used to store information about validation checks.
 *
 * Each status contains an outcome boolean and an error message.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/client/forms/validation
 */

 namespace client\form;

/**
 * The status class contains information about whether a validity check found any errors.
 *
 * This class contains two fields - the error status and the reason for error, if any.
 *
 * @since      1.0.0
 * @package    Biobank
 * @subpackage Biobank/client
 * @author     Nicholas Mamo <nicholas.mamo@um.edu.mt>
 */
class Status {

	/**
	 * A boolean indicating whether the validity check passed.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		boolean 	$status		The validity check status - true if it passed.
	 */
	protected $status;

	/**
	 * The error message associated with the failed validity check, if at all.
	 *
	 * @since	1.0.0
	 * @access	protected
	 * @var		boolean 	$message	The reason for the error, if the validity check failed.
	 */
	protected $message;

	/**
	 * Like exceptions, the result and message of a status are set in the constructor.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @var		boolean		$status		The validity check status.
	 * @var		string		$message	The reason for failure, if at all.
	 */
	public function __construct($status=true, $message="") {
		$this->status = $status;
		$this->message = $message;
	}

	/**
	 * Check whether the validity check repersented by this status was successful.
	 *
	 * @since	1.0.0
	 * @access	public
	 * @return	boolean		The validity check status - true if it was successful.
	 */
	public function is_successful() {
		return $this->status;
	}

	/**
	 * The string representation of the status is the message.
	 *
	 * @since	1.0.0
	 * @access public
	 * @return string		The textual representation of the status.
	 */
	public function __toString() {
		return $this->message;
	}

}

?>
