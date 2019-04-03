/**
 * Functions related to the triple field.
 * A triple field is made up of an attribute name and an attribute type.
 *
 * A third optional component is a list of constraints.
 * Some fields, like real numbers, have no constraints.
 * Some fields, like boolean fields, have implied constraints.
 * Enumerations have explicit constraints.
 *
 * Added attributes are sent to an area that shows the active attributes.
 * These attributes can be removed and re-added.
 */

var decremental_script = document.currentScript;
var decremental_script_directory = get_script_path(decremental_script);

jQuery(document).ready(function(){
	/*
	 * Upon initialization, improve usability of the triple.
	 * 	1. When a constraint is added via the `Enter` key, do not submit the form, but add the constraint.
	 * 	2. When an attribute is added via the `Enter` key, do not submit the form, but add the attribute.
	 *  3. When an attribute is added by clicking on the button, focus back on the text field, as if to add a new attribute.
	 *  4. When a constraint is added by clicking on the button, focus back on the text field, as if to add a new constraint.
	 */

	 /*
 	 * If `Enter` is pressed, add the constraint instead of submitting the form.
 	 */
	jQuery(".biobank-form-triple .select input.constraint[readonly!='readonly']").on("keydown", function(event) {
		if (event.key === "Enter") {
			add_constraint(jQuery(event.currentTarget));
			return false; // prevent the form from submitting
		}
	});

	/*
	* If `Enter` is pressed, add the attribute instead of submitting the form.
	*/
   jQuery(".biobank-form-triple .select .attribute input[type='text'][readonly!='readonly']").first().on("keydown", function(event) {
	   if (event.key === "Enter") {
		   add_triple_choice(jQuery(event.currentTarget));
		   return false; // prevent the form from submitting
	   }
   });

	/*
	 * Go through each triple and find the attribute section's `add` button, which should not have a `remove` class.
	 * From this element, navigate to the closest text field and focus back on it.
	 */
	jQuery(".biobank-form-triple .attribute input[type='button']:not(.remove)").on("click", function(event) {
		jQuery(event.currentTarget).closest(".attribute").find("input[type='text'][readonly!='readonly']").focus();
	});

	/*
	 * Go through each triple and find the constraints section's `add` button, which should not have a `remove` class.
	 * From this element, navigate to the closest text field and focus back on it.
	 */
	jQuery(".biobank-form-triple .options input[type='button']:not(.remove)").on("click", function(event) {
		jQuery(event.currentTarget).closest(".options").find("input.constraint[type='text'][readonly!='readonly']").focus();
	});

});

/**
 * Triggered when the user chooses a value from an incremental triple dropdown.
 *
 * @param	{DOM Element} dropdown - The selected dropdown button.
 */
function add_triple_choice(dropdown) {
	parent = jQuery(dropdown).closest(".select");
	select = parent.find("select");

	/*
	 * Load information about the plugin and the field.
	 */
	name = select.attr("name");
	plugin_name = get_plugin_name(name);
	field_name = get_field_name(name);

	/*
	 * Get the selected option.
	 */
	text_field = parent.find("input[type='text']").first();
	attribute_name = text_field.val();
	attribute_type = select.val(); // the actual type of the attribute, mirroring the API
	label = select.find(":selected").text(); // the pretty description of the type
	text_field.val("");

	if (attribute_name.length > 0) {
		/*
		 * Create a new field for the newly-created option.
		 */
		name_field = jQuery("<input>", {
			"name": plugin_name + "[chosen_" + field_name + "][name][" + attribute_name + "]",
			"readonly": true,
			"rvalue": attribute_name,
			"type": "text",
			"value": attribute_name
		});

		type_field = jQuery("<input>", {
			"name": plugin_name + "[chosen_" + field_name + "][type][" + attribute_name + "]",
			"readonly": true,
			"rvalue": attribute_type,
			"type": "text",
			"value": label
		});

		remove_button = jQuery("<input>", {
			"class": "button delete",
			"onclick": "remove_triple_choice(this);",
			"type": "button",
			"value": "Remove"
		});

		/*
		 * If this is a multi-choice field, fetch the options and list them.
		 */
		options = jQuery("<div>", {
	 		"class": "options"
	 	});

		if (label.toLowerCase() == "choice") {
			options.addClass("open"); // the list of options should be displayed; by default, it is closed
			wrapper = jQuery("<div>", { "class": "constraints" });
			jQuery.each(parent.find("div.options input.constraint"), function(index, element) {
				option = jQuery(element).val();
				if (option.length > 0) {
					input = jQuery("<input>", {
						"class": "constraint",
				   		"name": plugin_name + "[chosen_" + field_name + "][option][" + attribute_name + "][" + option + "]",
				   		"readonly": true, // WARNING: if the choices are not read-only, then the `rvalue` needs to be updated upon change
				   		"rvalue": option,
				   		"type": "text",
				   		"value": option
					});
					wrapper.append(input);
				}
			});
			options.append(jQuery("<label>").text("Options"));
			options.append(wrapper);

			/*
			 * Remove the inputted options since they will be added in a separate area.
			 * The field for new options is retained.
			 */
			parent.find("div.options input.constraint[readonly='readonly']").parent().remove();
		}

		area = jQuery("<div>", {
			"class": "selected"
		});
		area.append(name_field);
		area.append(type_field);
		area.append(remove_button);
		area.append(options);

		/*
		 * If there are already attributes, add the new attribute at the end.
		 * Otherwise, add the new attribute before the first one, so that it becomes first.
		 */
		if (parent.closest("td").find(".selected").length > 0) {
			area.insertAfter(parent.parent().find(".selected").last());
		} else {
			area.insertBefore(parent.parent().children().eq(0));
		}
	}
}

/**
 * Triggered when the user removes a value from an incremental triple dropdown.
 *
 * @param	{DOM Element} dropdown - The selected dropdown button.
 */
function remove_triple_choice(dropdown) {
	parent = jQuery(dropdown).closest("div");
	option = parent.find("input");

	/*
	 * Get the selected option and then remove the option
	 */
	attribute_type = option.attr("rvalue");
	label = option.val();
	parent.remove();
}

/**
 * Triggered when the user changes the selected field type.
 *
 * @param	{DOM Element} dropdown - The selected dropdown button.
 */
function change_attribute_type(dropdown) {
	parent = jQuery(dropdown).closest(".select");
	select = parent.find("select");
	name = select.attr("name");
	plugin_name = get_plugin_name(name);
	field_name = get_field_name(name);

	/*
	 * Get the selected option
	 */
	attribute_type = select.val();
	label = select.find(":selected").text();

	/*
	 * Toggle the display of the choices if need be.
	 */
	if (label.toLowerCase() == "choice") {
		parent.find(".options").show();
	} else {
		parent.find(".options").hide();
	}
}

/**
 * Triggered when the user adds a constraint to the triple.
 *
 * @param	{DOM Element} input - The selected input button.
 */
function add_constraint(input) {
	parent = jQuery(input).closest("div.options");
	text_field = parent.find("input[type='text']").first();
	plugin_name = get_plugin_name(name);
	field_name = get_field_name(name);

	/*
	 * Get the input and reset the field.
	 */
	constraint_name = text_field.val();
	text_field.val("");

	if (constraint_name.length > 0) {
		/*
		 * Create a new field for the input.
		 */
		input_field = jQuery("<input>", {
			"class": "constraint",
			"name": plugin_name + "[tentative_" + field_name + "][name][" + constraint_name + "]",
			"readonly": true,
			"rvalue": constraint_name,
			"type": "text",
			"value": constraint_name
		});

		remove_button = jQuery("<input>", {
			"class": "button delete",
			"onclick": "remove_triple_choice(this);",
			"type": "button",
			"value": "Remove"
		});

		area = jQuery("<div>");
		area.append(remove_button);
		area.append(input_field);
		parent.find(".constraints").append(area);
	}
}
