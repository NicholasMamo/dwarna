/*
 * Whenever any value of the quiz changes, check that it is correct.
 */
jQuery('#quiz input[type="radio"]').change((event) => {
	/*
	 * Get the user's choice and the actual answer.
	 */
	var choice = jQuery(event.target);
	var answer = jQuery(choice).closest('.question')
							   .find('input[type="hidden"]')
							   .val();

	/*
	 * Mark the question as correct or incorrect.
	 */
	if (choice.val() == answer) {
		choice.closest('.question')
			  .removeClass('incorrect');
	} else {
		choice.closest('.question')
			  .addClass('incorrect');
	}
});
