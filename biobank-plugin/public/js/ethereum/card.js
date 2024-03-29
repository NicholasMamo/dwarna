/**
 * This script asks Hyperledger to issue an identity and get a card.
 */

/**
 * A boolean that indicates whether the page is preparing to navigate.
 * If it is, further clicks to visit study pages are disabled.
 */
var navigating = false;

/**
 * Sleep for a number of milliseconds.
 *
 * From: https://stackoverflow.com/a/39914235
 *
 * @param {int}			ms - The number of milliseconds to sleep.
 * @return {Promise}	A promise which does nothing after sleeping.
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/*
 * If there is a consent field, load its value.
 */
jQuery('.study-consent').length && jQuery('.study-consent').ready(() => {
	console.log("HERE")
	var study_id = jQuery('input[name="biobank[study][study_id]"]').val();
	var access_token = decodeURIComponent(getCookie("access_token"));
	access_token = access_token.substring(2, access_token.indexOf("."));
	loadConsent(study_id).then(async function(response) {
		/*
			* Get the initial consent from the blockchain.
			* Depending on the consent, show or hide the quiz and enable or disable the form.
			*/
		var consent = false;
		if (response.length) {
			consent = response[0].status;

			/*
				* If the research partner can only withdraw consent, hide the quiz and enable the submit button.
				* Otherwise, show the quiz and leave the submit button disabled.
				*/
			if (consent) {
				jQuery('form').find('input[type="submit"]')
								.attr('disabled', null);
				jQuery('#biobank-consented').show();
				jQuery('#biobank-not-consented').hide();
				jQuery(`#biobank-study-${study_id}-consenting`).prop('checked', false);
			} else {
				jQuery('#biobank-quiz').show();
				jQuery('#biobank-consented').hide();
				jQuery('#biobank-not-consented').show();
				jQuery(`#biobank-study-${study_id}-consenting`).prop('checked', true);
			}
		} else {
			jQuery('#biobank-quiz').show();
			jQuery('#biobank-consented').hide();
			jQuery('#biobank-not-consented').show();
			jQuery(`#biobank-study-${study_id}-consenting`).prop('checked', true);
		}

		/*
			* After loading the consent, keep looking in case the last consent change has not been mined.
			*/
		for (var i = 0; i < 5; i++) {
			/*
				* Consent changes are loaded every second.
				*/
			await sleep(1000);
			new_consent = await loadConsent(study_id).then(async function(response) {
				if (response.length) {
					return response[0].status;
				}
			});

			/*
				* If the consent changed, update the quiz and the form.
				* This time, all of the form's components have to be updated.
				* In this way, the old setup is overriden.
				*/
			if (consent != new_consent) {
				consent = new_consent;

				/*
					* If the research partner can only withdraw consent, hide the quiz and enable the submit button.
					* Otherwise, show the quiz and leave the submit button disabled.
					*/
				if (consent) {
					jQuery('form').find('input[type="submit"]')
									.attr('disabled', null);
					jQuery('#biobank-quiz').hide();
					jQuery('#biobank-not-consented').hide();
					jQuery('#biobank-consented').show();
					jQuery(`#biobank-study-${study_id}-consenting`).prop('checked', false);
				} else {
					jQuery('#biobank-quiz').show();
					jQuery('#biobank-consented').hide();
					jQuery('#biobank-not-consented').show();
					jQuery(`#biobank-study-${study_id}-consenting`).prop('checked', true);
				}
				break;
			}
		}
	});
});

/**
 * Get the user's card for the study.
 * This card allows them to make requests to the Hyperledger API for this particular study.
 *
 * @param {object}	element - The study DOM element.
 * @param {int}		study_id - The study ID that is being loaded.
 */
function getCard(element, study_id) {
	/*
	 * If the user clicks on a study, get the card only if another card is not being fetched.
	 * This ensures that the research partner does not load one card and use it in the wrong study.
	 */
	if (! navigating) {
		navigating = true;
		jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
		jQuery(`${plugin_name}-get-card`).removeClass(`${plugin_name}-hidden`);
		jQuery.get(`${ajax_base_path}get_username.php`).then(function(response) {
			/*
			* First get the user's username.
			* If the user is logged in, check whether they have a temporary card for this study.
			* If they do not, a new card is created instead.
			*/
			if (response) {
				username = response;
				loadCard(study_id);
			} else {
				/*
				 * If the user is not logged in, check if they have an access token.
				 * If they do, clear that token and refresh the page for the change to take effect.
				 */
				if (getCookie(hyperledger_access_token)) {
					setCookie(hyperledger_access_token, "", 0);
					location.reload();
				}
			}
		});
	}
}

/**
 * Load the user's card if they have one.
 * This card allows them to make requests to the Ethereum API.
 *
 * @param {int}		study_id - The study ID that is being loaded.
 */
function loadCard(study_id) {
	var access_token = decodeURIComponent(getCookie(hyperledger_access_token));
	access_token = access_token.substring(2, access_token.indexOf("."));

	jQuery.get(`${ajax_base_path}has_card.php?temp=false&study_id=${study_id}`).then(function(response) {
		/*
		 * If the user has a credential card, load it.
		 * Otherwise, import the temporary card.
		 */
		if (response) {
			jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-get-credentials-card`).removeClass(`${plugin_name}-hidden`);
		} else {
			jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-get-temporary-card`).removeClass(`${plugin_name}-hidden`);
		}
		downloadCard(!response, study_id).then((card) => {
			jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-import-card`).removeClass(`${plugin_name}-hidden`);
			console.log("Address:", card)
			jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-save-card`).removeClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
			jQuery(`#${plugin_name}-redirect`).removeClass(`${plugin_name}-hidden`);
			jQuery(`#biobank-study-${study_id}-address`).val(card);
			jQuery('#biobank-study').val(study_id);
			console.log("Submitting form");
			jQuery('#study-form').submit();
			/*exportCard(access_token, study_id).then((card) => {
				getAddress(card).then((address) => {
					jQuery(`#${plugin_name}-alerts .${plugin_name}-alert`).addClass(`${plugin_name}-hidden`);
					jQuery(`#${plugin_name}-redirect`).removeClass(`${plugin_name}-hidden`);
					jQuery(`#biobank-study-${study_id}-address`).val(address);
					// saveCard(card, address).then((address) => {
					// 	jQuery('#biobank-study').val(study_id);
					// 	jQuery('#study-form').submit();
					// });
				});
			});*/
		});
	})
}

/**
 * Download the card from the backend.
 *
 * @param	{boolean}	temp - A boolean indicating whether the temporary or credentials card is being downloaded.
 * @param	{int}		study_id - The study ID that is being loaded.
 *
 * @return {object} The card promise response.
 */
function downloadCard(temp, study_id) {
	var request = new XMLHttpRequest();
	var access_token = decodeURIComponent(getCookie("access_token"));
	access_token = access_token.substring(2, access_token.indexOf("."));
	return new Promise((resolve, reject) => {
		/*
		 * Get the requested card from the backend.
		 */
		request.onreadystatechange = function() {
			if (request.readyState == 2) {
				if (request.status == 200) {
					request.responseType = "blob";
				} else {
					request.responseType = "text";
				}
			}

			if (request.readyState !== 4) { return; }

			if (request.status >= 200 && request.status < 300) {
				console.log("Got Private key", request.response.text())
				resolve(request.response.text())
			} else {
				reject({
					status: request.status,
					statusText: request.statusText
				});
			}
		};

		request.open("GET", `${ajax_base_path}get_card.php?temp=${temp ? "true" : "false"}&study_id=${study_id}`);
		request.send();
	});
}

/**
 *
 * @param {Blob}	card - The card to save in the database.
 *
 * @return {object} The address promise response.
 */
function getAddress(card) {
	var card = new Blob([card], {type: "application/octet-stream"});

	var reader = new FileReader();
	return new Promise((resolve, reject) => {
		reader.addEventListener("loadend", function() {
			JSZip.loadAsync(reader.result).then(function (zip) {
				return zip.file('metadata.json').async("text");
			}).then(function (data) {
				var metadata = JSON.parse(data);
				return resolve(metadata.userName);
			})
		});
		reader.readAsArrayBuffer(card);
	});
}

/**
 * Load the consent status of the user from the current card.
 *
 * @param {int}		study_id - The study for which the consent status will be loaded.
 *
 * @return {object} The consent promise response.
 */
async function loadConsent(study_id) {
	var access_token = decodeURIComponent(getCookie(hyperledger_access_token));
	access_token = access_token.substring(2, access_token.indexOf("."));

	console.log("Loading consent")
	return jQuery.get(`${ajax_base_path}has_consent.php?study_id=${study_id}`)
}

/**
* Get the value of the cookie having the given name.
* Based on https://stackoverflow.com/a/1599291/1771724
*
* @param	{string} name - The name of the cookie whose value to retrieve.
*
* @return	{string|null} The cookie's value, or null if no cookie with the given name is found.
*/
function getCookie(name) {
	var cookie_name = name + "=";
	var cookies = document.cookie.split(";");
	for (var i = 0; i < cookies.length; i++) {
		cookie = cookies[i].trim();
		if (cookie.indexOf(cookie_name) == 0) {
			return cookie.substring(cookie_name.length);
		}
	}
	return null;
}

/**
* Set the value of the cookie having the given name.
* Based on https://stackoverflow.com/a/24103596/1771724
*
* @param	{string} name - The name of the cookie whose value to set.
* @param	{string} value - The cookie's value.
* @param	{int} days - The number of days for which the cookie should be valid.
*/
function setCookie(name, value, days) {
	var expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
	document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/`;
}

