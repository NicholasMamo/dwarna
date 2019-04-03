/*
 * Functions related to the decremental field.
 * A decremental field is made up of a dropdown (select) element and a button.
 * Whenever the button is added, the currently-selected option is added to an area of selected options.
 * Most importantly, once this option is chosen, it cannot be chosen again - it is removed from the dropdown.
 */

var decremental_script = document.currentScript;
var decremental_script_directory = get_script_path(decremental_script);

jQuery.getScript(decremental_script_directory + "../forms.js", function () { });

/**
 * Triggered when the user chooses a value from an incremental dropdown.
 *
 * @param	{DOM Element} dropdown - The selected dropdown button.
 */
function add_decremental_choice(dropdown) {
	parent = jQuery(dropdown).closest("div");
	select = parent.find("select");
	name = select.attr("name");
	plugin_name = get_plugin_name(name);
	field_name = get_field_name(name);

	/*
	 * Get the selected option and remove it from the dropdown
	 */
	selection = select.val();
	label = select.find(":selected").text();
	select.find("option[value='" + selection + "']").remove();

	/*
	 * Create a new field for the removed option
	 */
	text_field = jQuery("<input>", {
		"name": plugin_name + "[chosen_" + field_name + "][" + selection + "]",
		"readonly": true,
		"rvalue": selection,
		"type": "text",
		"value": label
	});

	remove_button = jQuery("<input>", {
		"class": "button delete",
		"onclick": "remove_decremental_choice(this);",
		"type": "button",
		"value": "Remove"
	});

	area = jQuery("<div>", {
		"class": "selected"
	});
	area.append(text_field);
	area.append(remove_button);
	area.insertBefore(parent);

	/*
	 * Hide the dropdown if there is nothing left to choose
	 */
	if (select.find("option").length == 0) {
		parent.hide();
	}
}

/**
 * Triggered when the user removes a value from an incremental dropdown.
 *
 * @param	{DOM Element} dropdown - The selected dropdown button.
 */
function remove_decremental_choice(dropdown) {
	parent = jQuery(dropdown).closest("div");
	option = parent.find("input");
	select = parent.parent().find("select");

	/*
	 * Get the selected option and then remove the option
	 */
	selection = option.attr("rvalue");
	label = option.val();
	parent.remove();

	/*
	 * Add the option to the dropdown
	 */
	select.append(jQuery("<option>", {
		"value": selection
	}).text(label));

	/*
	 * Hide the dropdown if there is nothing left to choose
	 */
	if (select.find("option").length == 1) {
		select.parent().show();
	}
}
