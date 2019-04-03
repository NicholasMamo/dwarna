<?php

namespace fields;

/**
 * Provides custom field types.
 *
 * The functions in this file provide new form fields.
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin/partials
 */

 /**
  * Create a select menu that displays only selections.
  *
  * @since	1.0.0
  * @param	string	$name		The field name.
  * @param	array	$loaded		A list of choices that have been selected.
  *
  * @return  string	The HTML string of the select
  */
 function decremental_list($loaded=array()) {
 	/*
 	 * Load the elements that have already been chosen.
 	 */
 	$loaded_string = "";
 	foreach($loaded as $id => $option) {
 		$loaded_string .= "
 		<div class='wide selected'>
 			<input name='biobank[chosen_researchers][$id]' readonly='readonly' rvalue='$id' type='text' value='$option'>
 		</div>";
 	}

 	return "
 		$loaded_string";
 }

/**
 * Create a select menu that allows multiple selections.
 *
 * @since	1.0.0
 * @param	array	$options	An associative array of id, display pairs.
 * @param	array	$loaded		A list of choices that have already been selected.
 *
 * @return  string	The HTML string of the select
 */
function decremental_select($name, $options, $loaded=array()) {
	/*
	 * First load the elements that have already been chosen.
	 */
	$loaded_string = "";
	foreach($loaded as $id => $option) {
		$loaded_string .= "
		<div class='selected'>
			<input name='biobank[chosen_researchers][$id]' readonly='readonly' rvalue='$id' type='text' value='$option'>
			<input class='button delete' onclick='remove_decremental_choice(this);' type='button' value='Remove'>
		</div>";
	}

	/*
	 * Then load the elements that have not been chosen.
	 */
	$option_string = "";
	foreach($options as $id => $option) {
		if (! in_array($option, $loaded, true)) {
			$option_string .= "<option value='$id'>$option</option>";
		}
	}

	/*
	 * Construct the final string.
	 */
	return "
		$loaded_string
		<div class='select' " . (strlen($option_string) == 0 ? "style='display: none;'" : "") . ">
			<select class='biobank-decremental-select' name='$name'>$option_string</select>
			<input class='button' onclick='add_decremental_choice(this);' type='button' value='Add' />
		</div>";
}

/**
 * Create a select menu that allows multiple named selections.
 *
 * @since	1.0.0
 * @param	string	$name		The field name.
 * @param	array	$options	An associative array of id, display pairs.
 * @param	array	$loaded		A list of choices that have already been selected.
 *
 * @return  string	The HTML string of the select.
 */
function triple($name, $options, $loaded=array()) {
	/*
	 * First load the chosen attributes.
	 */
	$selected = "";
	foreach ($loaded as $attribute) {
		$attribute_name = $attribute->name;
		$attribute_type = $attribute->type;
		$label = isset($options[$attribute_type]) ? $options[$attribute_type] : "Unknown";
		$options_string = "";
		if ($attribute_type == "ENUMERATION") {
			$option_string = "";
			foreach ($attribute->constraints as $option) {
				$options_string .= "<input class='constraint' name='biobank[chosen_attributes][option][$attribute_name][$option]' readonly='readonly' rvalue='$option' type='text' value='$option' />";
			}

			$options_string = "
			<label>Options</label>
				<div class='constraints'>
				$options_string
			</div>";
		}

		$selected .= "
		<div class='selected'>
			<input name='biobank[chosen_attributes][name][$attribute_name]' readonly='readonly' rvalue='$attribute_name' type='text' value='$attribute_name'>
			<input name='biobank[chosen_attributes][type][$attribute_name]' readonly='readonly' rvalue='$attribute_type' type='text' value='$label'>
			<input class='button delete' onclick='remove_triple_choice(this);' type='button' value='Remove'>
			<div class='options " . ($attribute_type == "ENUMERATION" ? "open" : "") . "'>
				$options_string
			</div>
		</div>";
	}

	/*
	 * Then load the options for a new attribute.
	 */
	$option_string = "";
	foreach($options as $id => $option) {
		$option_string .= "<option value='$id'>$option</option>\n";
	}

	/*
	* Create the entire area.
	*/
	return "
		$selected
		<hr/>
		<div class='select' " . (strlen($option_string) == 0 ? "style='display: none;'" : "") . ">
			<div class='attribute'>
				<input type='text' id='$name' />
				<select class='biobank-triple-select' name='$name' onchange='change_attribute_type(this);'>
					$option_string
				</select>
				<input class='button' onclick='add_triple_choice(this);' type='button' value='Add' />
			</div>
			<div class='options " . (strtolower(array_values($options)[0]) == "choice" ? "open" : "") . "'>
				<div>
					<label for='$name-option'>Options</label>
					<div class='constraints'>
						<input class='constraint' type='text' id='$name-option' />
						<input class='button' onclick='add_constraint(this);' type='button' value='Add' />
					</div>
				</div>
			</div>
		</div>";
}

?>
