<?php

$notices = array(
	"update" => "updated",
	"remove" => "removed",
	"create" => "created",
	"creating" => "is being created",
);

/**
 * Preprocess the message.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 *
 * @return  string      The preprocessed string
 */
function preprocess($message) {
	$punctuation = array('.', '?', '!');
	$message = in_array(substr($message, -1), $punctuation) ? $message : "$message.";
	return $message;
}

/**
 * Create a WordPress notice.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 * @var     string      $class          The class of the notice - choice among error, warning, info and success (from https://codex.wordpress.org/Plugin_API/Action_Reference/admin_notices)
 *
 * @return  string      The HTML string of the notice
 */
function create_notice($message, $class) {
	$message = preprocess($message);
	if (is_admin()) {
    	return "<div class = 'notice notice-$class'><p>$message</p></div>";
	} else {
		return "<div class = 'biobank-alert biobank-alert-$class'>$message</div>";
	}
}

/**
 * Create a WordPress success notice.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 *
 * @return  string      The HTML string of the success notice
 */
function create_success_notice($message) {
    return create_notice($message, "success");
}

/**
 * Create a WordPress info notice.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 *
 * @return  string      The HTML string of the info notice
 */
function create_info_notice($message) {
    return create_notice($message, "info");
}

/**
 * Create a WordPress warning notice.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 *
 * @return  string      The HTML string of the warning notice
 */
function create_warning_notice($message) {
    return create_notice($message, "warning");
}

/**
 * Create a WordPress error notice.
 *
 * @since   1.0.0
 * @var     string      $message        The message to display
 *
 * @return  string      The HTML string of the error notice
 */
function create_error_notice($message) {
    return create_notice($message, "error");
}

?>
