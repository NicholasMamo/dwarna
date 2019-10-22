jQuery(document).ready(() => {
	/*
	 * When the document loads, add click behavior to the recipient removal button.
	 */
	jQuery('.recipient .icon-remove').on('click', (event) => {
		jQuery(event.currentTarget).closest('.recipient').remove();
	});
});

/*
 * When the form is submitted, prepare the email.
 * This process copies the HTML write-up to an input field so it can be processed.
 */
jQuery('#biobank-email-form').on('submit', (event) => {
	prepareEmail();
});

/*
 * When the recipient field receives input, check if the email address has ended.
 * If it has, reset the field and add the email address as a new recipient.
 */
jQuery('#biobank-recipient').on('input', (event) => {
	/*
	 * Get the value and the last inputted character.
	 */
	var value = jQuery('#biobank-recipient').val();
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
		jQuery('#biobank-recipient').val('');

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
jQuery('#biobank-recipient').on('blur', (event) => {
	/*
	 * Get the value.
	 */
	var value = jQuery('#biobank-recipient').val();
	var email_pattern = /^[0-9a-z.]+@[0-9a-z]+(\.[a-z]+)+$/gi;

	/*
	 * If the input is an email address, add the email address as a recipient.
	 */
	if (email_pattern.test(value)) {
		/*
		 * Then, reset the field and add the recipient.
		 */
		jQuery('#biobank-recipient').val('');
		addRecipient(value);
	}
});

/**
 * Add a recipient to the list of recipients.
 * The recipient is made of a hidden input value, the email address as text and a removal button.
 */
function addRecipient(email) {
	var input = jQuery('<input>').attr('type', 'hidden')
							.attr('name', 'recipient[]')
							.val(email);
	var remove = jQuery("<span>").addClass('fa fa-times-circle icon-remove')
							.on('click', (event) => {
								jQuery(event.currentTarget).closest('.recipient').remove();
							});
	var recipient = jQuery('<div>').addClass('recipient')
							  .text(email)
							  .append(input)
							  .append(remove);
	jQuery('#biobank-recipients').append(recipient);
}

/**
 * Prepare the email for submission.
 * All this function does is copy the HTML content of the body into the accompanying text field.
 */
function prepareEmail() {
	jQuery('#biobank-body-input').val(
		jQuery('iframe#biobank-body_ifr').contents()
										 .find('[data-id="biobank-body"]')
										 .html());
}
