/*
 * Whenever any value of the quiz changes, check that it is correct.
 */
jQuery('#biobank-quiz input[type="radio"]').change((event) => {
	/*
	 * Mark the question as correct or incorrect.
	 */
	var question = jQuery(event.target).closest('.biobank-question');
	if (isCorrect(question)) {
		question.removeClass('incorrect');
	} else {
		question.addClass('incorrect');
	}

	enableForm(question.closest('form'));
});

/*
 * Disable the submit button if there are any incorrect questions.
 * The form should also be disabled if there are unanswered questions.
 * The form is enabled first, and then disabled if need be.
 *
 * @param {object}	form - The form DOM element.
 */
function enableForm(form) {
	form.find('input[type="submit"]')
		.attr('disabled', null);

	/*
	 * Check if there are any wrong questions.
	 */
	jQuery('.biobank-question').each((index, question) => {
		question = jQuery(question);
		if (question.hasClass('incorrect') ||
			! jQuery(question).find('input:checked').length) {
			question.closest('form')
					.find('input[type="submit"]')
					.attr('disabled', true);
		}
	});
}

/**
 * Check whether the question in the given element is correct.
 *
 * @param {object}		question - The question DOM element.
 * @return {boolean}	A boolean indicating whether the question is marked correctly.
 */
function isCorrect(question) {
	/*
	 * Get the user's choice and the actual answer.
	 */
	var choice = jQuery(question).find('input:checked');
	var answer = jQuery(question).find('input[type="hidden"]')
								 .val();
	return choice.val() == answer;
}
