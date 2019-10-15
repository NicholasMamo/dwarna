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
});
