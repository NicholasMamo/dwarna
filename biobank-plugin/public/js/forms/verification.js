/*
 * Functions that are used to verify form input.
 * Each function is attached to one particular form.
 */

/**
 * Verify the consent form that is submitted by the user.
 * The function ensures that the password field is not empty.
 * The verification happens in the frontend so that the user's choices are not lost.
 * @return	{boolean} A boolean indicating whether the inputs are filled in correctly.
 */
function verify_consent_form() {
	is_password_empty = jQuery("input[type='password']").val().length == 0;
	if (is_password_empty) {
		jQuery("input[type='password']").closest("tr").find(".error").show();
	}

	return !is_password_empty;
}
