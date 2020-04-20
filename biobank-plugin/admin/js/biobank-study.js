/*
 * When the form is submitted, prepare the study.
 * This process copies the HTML write-up to an input field so it can be processed.
 */
jQuery('#biobank-study-form').on('submit', (event) => {
	prepareStudy();
	console.log(jQuery('#biobank-description-input').val());
});

/**
 * Prepare the study for submission.
 * All this function does is copy the HTML content of the body into the accompanying text field.
 */
function prepareStudy() {
	jQuery('#biobank-description-input').val(
		jQuery('iframe#biobank-description_ifr').contents()
										 .find('[data-id="biobank-description"]')
										 .html());
}
