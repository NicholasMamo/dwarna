<?php

namespace fields;

/**
 * Generates fields to be used in the frontend.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/public/partials
 */

/**
 * Create a field from an attribute.
 * This function parses the type and uses the attributes to create a form field.
 *
 * @since	1.0.0
 * @param	string	$plugin		The name of the plugin.
 * @param	string	$study		The study's unique ID.
 * @param	string	$attribute	The type of the field.
 * @param	array	$defaults	An associative array containing a list of defaults, first separated by name, then by type.
 *
 * @return  string	The HTML string of the field.
 */
function create_form_field($plugin, $study, $attribute, $defaults=array()) {
	$field="";

	/*
	 * Load the information about the new field.
	 */
	$id=(string) $attribute->attribute_id;
	$name=$attribute->name;
	$type=$attribute->type;
	$constraints=$attribute->constraints;

	$defaults=(array) $defaults;
	$default=isset($defaults[$id]) ? $defaults[$id] : "";

	switch (strtoupper($type)) {
		case "INTEGER":
			return integer_field($id, $plugin . "[$study][attributes][$id]", $default);
		case "REAL":
			return real_field($id, $plugin . "[$study][attributes][$id]", $default);
		case "BOOLEAN":
			return boolean_field($id, $plugin . "[$study][attributes][$id]", $default);
		case "ENUMERATION":
			return enumeration_field($id, $plugin . "[$study][attributes][$id]", $default, $constraints);
		case "STRING":
			return text_field($id, $plugin . "[$study][attributes][$id]", $default, $constraints);
	}

	return $field;
}

/**
 * Create an integer field.
 *
 * @since	1.0.0
 * @param	string	$id			The field's unique ID.
 * @param	string	$name		The field name.
 * @param	string	$value		The field's default value.
 *
 * @return  string	The HTML string of the field.
 */
function integer_field($id, $name, $value) {
	$input_string = "<input id='$id' name='$name' type='number' step='1' value='" . (int) $value . "'>";
	return $input_string;
}

/**
 * Create a real field.
 *
 * @since	1.0.0
 * @param	string	$id			The field's unique ID.
 * @param	string	$name		The field name.
 * @param	string	$value		The field's default value.
 *
 * @return  string	The HTML string of the field.
 */
function real_field($id, $name, $value) {
	$input_string = "<input id='$id' name='$name' type='number' step='any' value='" . $value . "'>";
	return $input_string;
}

/**
 * Create a boolean choice field.
 *
 * @since	1.0.0
 * @param	string	$id			The field's unique ID.
 * @param	string	$name		The field name.
 * @param	string	$value		The field's default value.
 *
 * @return  string	The HTML string of the field.
 */
function boolean_field($id, $name, $value) {
	// NOTE: A hidden checkbox is added so that the value is always sent to the backend
	$input_string = "<input name='$name' type='hidden' value='0'>";
	$input_string .= "<input id='$id' name='$name' type='checkbox' " . ($value == True ? "checked" : "") . ">";
	return $input_string;
}

/**
 * Create an enumeration choice field.
 * This is based on a select field.
 *
 * @since	1.0.0
 * @param	string	$id			The field's unique ID.
 * @param	string	$name		The field name.
 * @param	string	$value		The field's default value.
 * @param	array	$options	The field's possible options.
 *
 * @return  string	The HTML string of the field.
 */
function enumeration_field($id, $name, $value, $options) {
	$option_string = "";
	foreach ($options as $option) {
		$option_string .= "<option value='$option' " . ($value == $option ? "selected" : "") . ">$option</option>\n";
	}

	$select_wrapper = "<select id='$id' name='$name'>$option_string</select>";
	return $select_wrapper;
}

/**
 * Create a text field.
 *
 * @since	1.0.0
 * @param	string	$id			The field's unique ID.
 * @param	string	$name		The field name.
 * @param	string	$value		The field's default value.
 *
 * @return  string	The HTML string of the field.
 */
function text_field($id, $name, $value) {
	$input_string = "";
	$input_string .= "<input id='$id' name='$name' type='text' value='$value'>";
	return $input_string;
}

?>
