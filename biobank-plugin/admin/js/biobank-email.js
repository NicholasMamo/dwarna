$(document).ready(() => {
	/*
	 * When the document loads, add click behavior to the recipient removal button.
	 */
	$('.recipient .icon-remove').on('click', (event) => {
		$(event.currentTarget).closest('.recipient').remove();
	});
});

/*
 * When the recipient field receives input, check if the email address has ended.
 * If it has, reset the field and add the email address as a new recipient.
 */
$('#recipient').on('input', (event) => {
	/*
	 * Get the value and the last inputted character.
	 */
	var value = $('#recipient').val();
	var last = value.slice(-1);

	/*
	 * If the last character is not email-acceptable, assume the email address has ended.
	 */
	if (! /[a-z0-9_@.]/i.test(last)) {
		/*
		 * Remove the last-inputted character.
		 * Then, reset the field and add the recipient.
		 */
		value = value.slice(0, -1);
		$('#recipient').val('');

		/*
		 * If the assumed email address is not empty, proceed to add the email address as a recipient.
		 */
		if (value.length) {
			addRecipient(value);
		}
	}
});

/*
 * When the recipient field loses focus, check whether the input is an email address.
 * If it is, add as a recipient.
 */
$('#recipient').on('blur', (event) => {
	/*
	 * Get the value.
	 */
	var value = $('#recipient').val();
	var email_pattern = /^[0-9a-z.]+@[0-9a-z]+(\.[a-z]+)+$/gi;

	/*
	 * If the input is an email address, add the email address as a recipient.
	 */
	if (email_pattern.test(value)) {
		/*
		 * Then, reset the field and add the recipient.
		 */
		$('#recipient').val('');
		addRecipient(value);
	}
});

/**
 * Add a recipient to the list of recipients.
 * The recipient is made of a hidden input value, the email address as text and a removal button.
 */
function addRecipient(email) {
	var input = $('<input>').attr('type', 'hidden')
							.attr('name', 'recipient[]')
							.val(email);
	var remove = $("<span>").addClass('fa fa-times-circle icon-remove')
							.on('click', (event) => {
								$(event.currentTarget).closest('.recipient').remove();
							});
	var recipient = $('<div>').addClass('recipient d-inline-block')
							  .text(email)
							  .append(input)
							  .append(remove);
	$('#recipients').append(recipient);
}

/**
 * Prepare the email for submission.
 * All this function does is copy the HTML content of the body into the accompanying text field.
 */
function prepareEmail() {
	$('#email-body-input').val($('#email-body').html());
}

/*********************
 *     Validation    *
 *********************/

/**
 * Validate the email form before submitting.
 *
 * @return {bool} A boolean indicating whether the form is valid.
 */
function validate_email_form() {
	var valid = true;

	/*
	 * First go through the individual fields that need validation.
	 * These validations remove any error feedback.
	 *
	 * In case some fields require multiple error validation, they are chained together.
	 * In this way, if one fails, subsequent ones do not clear the previous error.
	 *
	 * Finally, validate required fields.
	 */
	$("form.needs-validation").each((index, form) => {
		/*
		 * Hide all errors on the form.
		 */
		valid = true;
		$(form).find('.invalid-feedback').addClass('d-none');

		valid = validate_required(form) && valid;
		valid = validate_body_filled(form) && valid;

		var recipients = $(form).find(".recipient");
		valid = validate_recipients(recipients) && valid;

		$(form).addClass("was-validated");
	});

	return valid;
}

/**
 * Validate the email unsubscription form before submitting.
 *
 * @return {bool} A boolean indicating whether the form is valid.
 */
function validate_unsubscription_form() {
	var valid = true;

	/*
	 * First go through the individual fields that need validation.
	 * These validations remove any error feedback.
	 *
	 * In case some fields require multiple error validation, they are chained together.
	 * In this way, if one fails, subsequent ones do not clear the previous error.
	 *
	 * Finally, validate required fields.
	 */
	$("form.needs-validation").each((index, form) => {
		/*
		 * Hide all errors on the form.
		 */
		valid = true;
		$(form).find('.invalid-feedback').addClass('d-none');

		valid = validate_required(form) && valid;

		var email = $(form).find("input[required][name$='email']");
		valid = validate_email(email) && valid;

		$(form).addClass("was-validated");
	});

	return valid;
}

/**
 * Validate that the required fields are filled in.
 *
 * @param {Object}	form 	The form to validate.
 *
 * @return {bool} A boolean indicating whether there were any invalid fields.
 */
function validate_required(form) {
	var valid = true;
	$(form).find("input[required]").each((index, element) => {
		if (! $(element).val()) {
			$(element).parent()
					  .find('.invalid-feedback.invalid-feedback-required')
					  .removeClass('d-none');
			valid = false;
		}
	});
	return valid;
}

/**
 * Validate that the body is not empty.
 *
 * @param {Object}	form 	The form to validate.
 *
 * @return {bool} A boolean indicating whether there were any invalid fields.
 */
function validate_body_filled(form) {
	var valid = true;

	$(form).find('#email-body').each((index, element) => {
		/*
		 * The validation is based on the text itself.
		 * If there is no visible text, then the body is considered to be empty.
		 */
		if (! $(element).text()) {
			$(element).parent()
					  .find('.invalid-feedback.invalid-feedback-required')
					  .removeClass('d-none');
			$("#email-body-input").addClass('is-invalid');
			valid = false;
		}
	});

	return valid;
}

/**
 * Validate the recipient email address.
 *
 * @param {Object}	recipients	The recipient email addresses to validate.
 *
 * @return {bool} A boolean indicating whether the email address is valid.
 */
function validate_recipients(recipients) {
	var valid = true;
	var email_pattern = /^[0-9a-z.]+@[0-9a-z]+(\.[a-z]+)+$/gi; // the validation pattern

	/*
	 * If there are no recipients, there is nothing to validate, so return.
	 */
	if (! recipients.length) {
		return valid;
	}

	/*
	* Clear any errors on the field.
	*/
	var email_field = $(recipients).closest('.form-group')
								   .find('input');
	$(email_field).get(0).setCustomValidity("");
	$(recipients).each((index, recipient) => {
		/*
		* If the pattern does not match, show an errrecipient.
		*/
		if (! $(recipient).text().trim().match(email_pattern)) {
			var message = "Invalid email address";
			$(email_field).get(0).setCustomValidity(message)
			$(email_field).addClass('is-invalid');
			$(email_field).parent()
						  .find(".invalid-feedback.invalid-feedback-format")
						  .removeClass('d-none');
			$(recipient).addClass('recipient-invalid');
			valid = false;
		} else {
			$(recipient).removeClass('.recipient-invalid');
		}
	})

	return valid;
}
