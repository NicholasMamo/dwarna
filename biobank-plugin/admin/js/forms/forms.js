/*
 * General functions related to forms.
 */

jQuery(document).ready(function(){
	/*
	 * Upon initialization, the first thing to do is convert date fields into actual calendars.
	 */
	load_calendars();
});

/**
 * Show the password in the text field.
 * This is a fix that happens when using WordPress' own password generator.
 * Upon clicking on `Generate` the first time, the password is shown.
 * After clicking `cancel` and then `Generate` again, the password field is empty, though only visibly - the password is still there.
 * The error occurs when creating a new profile, not when updating it.
 */
function show_password() {
	jQuery("#pass1").next().val(jQuery("#pass1").val())
}

/**
 * Convert date fields into actual calendars.
 */
function load_calendars() {
	jQuery(".biobank-datepicker").each(function(){
	    jQuery(this).datepicker({
			dateFormat : "dd-mm-yy"
		});
	});
}

/*
 * General form functions.
 */

/**
 * Extract the field name from the given name
 *
 * @param	{string} name - The full field name.
 * @return	{string} The field name.
*/
function get_field_name(name) {
	return name.substring(name.search("\\[") + 1, name.search("\\]"));
}

/**
 * Extract the plugin name from the given name
 *
 * @param	{string} name - The full field name.
 * @return	{string} The plugin name.
 */
function get_plugin_name(name) {
	return name.substring(0, name.search("\\["));
}

/**
 * Triggered when the user submits the form.
 * Copies the real values (rvalue) into the value fields of text fields.
 *
 * @param	{DOM Element} input - The selected input button.
 */
function convert_values() {
	/*
	 * Retain only elements that do not have an undefined real value.
	 */
	elements = jQuery("input[type='text']").filter(function(index, element) {
		rval = jQuery(element).attr("rvalue");
		return (typeof rval !== typeof undefined && rval !== false);
	});

	jQuery.each(elements, function(index, element) {
		jQuery(element).val(jQuery(element).attr("rvalue"));
	});
}
