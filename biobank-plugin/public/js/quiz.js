/*
 * Whenever any value of the quiz changes, check that it is correct.
 */
jQuery('#biobank-quiz input[type="radio"]').change((event) => {
	/*
	 * Get the user's choice and the actual answer.
	 */
	var choice = jQuery(event.target);
	var answer = jQuery(choice).closest('.biobank-question')
							   .find('input[type="hidden"]')
							   .val();

	/*
	 * Mark the question as correct or incorrect.
	 */
	if (choice.val() == answer) {
		choice.closest('.biobank-question')
			  .removeClass('incorrect');
	} else {
		choice.closest('.biobank-question')
			  .addClass('incorrect');
	}

	/*
	 * Disable the submit button if there are any incorrect questions.
	 */
	if (jQuery('.biobank-question.incorrect').length) {
		choice.closest('form')
			  .find('input[type="submit"]')
			  .attr('disabled', true);
	} else {
		choice.closest('form')
			  .find('input[type="submit"]')
			  .attr('disabled', null);
	}
});
