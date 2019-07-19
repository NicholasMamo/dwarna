/**
 * This script asks Hyperledger to issue an identity and get a card.
 */

/**
 * The Hyperledger Composer API key name.
 */
const hyperledger_access_token = "access_token";

/**
 * The port where the Python REST API is listening.
 */
const biobank_backend_port = 7225;

/**
 * The port where the Hyperledger multi-user REST API is listening.
 */
const hyperldger_port = 3000;

/**
 * The website host.
 */
const host = `${window.location.protocol}//${window.location.hostname}`;

/**
 * The base path where the AJAX scripts reside.
 */
const ajax_base_path = `${host}/wordpress/wp-content/plugins/biobank-plugin/public/ajax/`;

/**
* When the document loads, check import the user's card.
*/
jQuery(document).ready(function(){
	if (false) {
		jQuery.get(`${ajax_base_path}get_username.php`).then(function(response) {
			if (response) {
				console.log("Loading card");
				username = response;
				loadCard();
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
});

/**
 * Get the user's card for the study.
 * This card allows them to make requests to the Hyperledger API for this particular study.
 *
 * @param {object}	element - The study DOM element.
 * @param {int}		study_id - The study ID that is being loaded.
 */
function getCard(element, study_id) {
	if (jQuery(element).attr('aria-expanded') == 'false') {
		/*
		 * Whenever a study is opened, get the card.
		 * Otherwise, do nothing.
		 */
		console.log(`Getting card for study ${study_id}`);

		jQuery.get(`${ajax_base_path}get_username.php`).then(function(response) {
			/*
			* First get the user's username.
			* TODO: Check the user role as well.
			*
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
 * This card allows them to make requests to the Hyperledger API.
 *
 * @param {int}		study_id - The study ID that is being loaded.
 */
function loadCard(study_id) {
	var access_token = decodeURIComponent(getCookie(hyperledger_access_token));
	access_token = access_token.substring(2, access_token.indexOf("."));

	var request = new XMLHttpRequest();
	request.open("GET", `${host}:${hyperldger_port}/api/wallet/card`, true);
	request.setRequestHeader("X-Access-Token", access_token);
	request.onreadystatechange = function() {
		if(this.readyState == 4) {
			if (this.status == 200) {
				ping().then(function(response) {
					console.log(typeof(response));
					console.log("System pinged");
					console.log("Getting already-imported card");
					exportCard(access_token);
				});
			} else {
				jQuery.get(`${ajax_base_path}has_card.php?temp=false&study_id=${study_id}`).then(function(response) {
					/*
					 * If the user has a credential card, load it.
					 * Otherwise, import the temporary card.
					 */
					if (response) {
			 			console.log("Getting credentials card");
			 			importCard(false, study_id);
					} else {
						console.log("Getting temporary card");
						importCard(true, study_id);
			 		}
				});
			}
		}
	}
	request.send(null);
}

/**
 * When a card is found, load it and import it into the authenticated user's wallet.
 *
 * @param	{boolean}	temp - A boolean indicating whether the temporary or credentials card is being loaded.
 * @param	{int}		study_id - The study ID that is being loaded.
 */
function importCard(temp, study_id) {
	var request = new XMLHttpRequest();
	var access_token = decodeURIComponent(getCookie("access_token"));
	access_token = access_token.substring(2, access_token.indexOf("."));
	/*
	 * Get the requested card from the backend.
	 */
	request.open("GET", `${ajax_base_path}get_card.php?temp=${temp ? "true" : "false"}&study_id=${study_id}`, true);
	request.onreadystatechange = function(){
		if(this.readyState == 4) {
			if(this.status == 200) {
				var blob = new Blob([this.response], {type: "application/octet-stream"});
				var card_data = blob;
				const file = new File(
					[card_data], "card.card",
					{type: "application/octet-stream", lastModified: Date.now()}
				);

				const formData = new FormData();
				formData.append("card", file);
				jQuery.ajax({
					url: `${host}:${hyperldger_port}/api/wallet/import?name=card`,
					method: "POST",
					type: "POST",
					cache: false,
					data: formData,
					processData: false,
					contentType: false,
					headers: {
						"X-Access-Token": access_token,
					},
				}).then(function(response) {
					console.log("Card imported")
					ping().then(function(response) {
						console.log("System pinged");
						exportCard(access_token);
					});
				});
			} else if(this.responseText != "") {
				console.log(this.responseText);
			}
		} else if(this.readyState == 2) {
			if (this.status == 200) {
				this.responseType = "blob";
			} else {
				this.responseType = "text";
			}
		}
	};
	request.send(null);
}

/**
 * Export the user's card.
 *
 * @param	{string} access_token - The user's Hyperledger access token.
 *									This token is stored as a cookie.
 */
function exportCard(access_token) {
	var request = new XMLHttpRequest();
	request.open("GET", `${host}:${hyperldger_port}/api/wallet/card/export`, true);
	request.setRequestHeader("X-Access-Token", access_token);
	request.onreadystatechange = function(){
		if(this.readyState == 4) {
			if(this.status == 200) {
				console.log("Card exported");

				var blob = new Blob([this.response], {type: "application/octet-stream"});
				var card = blob;

				var reader = new FileReader();
				reader.addEventListener("loadend", function() {
					JSZip.loadAsync(reader.result).then(function (zip) {
						return zip.file('metadata.json').async("text");
				    }).then(function (data) {
						var metadata = JSON.parse(data);
						return metadata.userName;
					});
				});
				reader.readAsArrayBuffer(blob);
			} else if(this.responseText != "") {
				console.log(this.responseText);
			}
		} else if(this.readyState == 2) {
			if (this.status == 200) {
				this.responseType = "blob";
			} else {
				this.responseType = "text";
			}
		}
	};
	request.send(null);
}

/**
 * Save the credential-ready card to the backend.
 */
function saveCard(card) {
	const file = new File(
		[card], "card.card",
		{type: "application/octet-stream", lastModified: Date.now()}
	);
	const formData = new FormData();
	formData.append("card", file);
	jQuery.ajax({
		url: `${ajax_base_path}save_card.php`,
		method: "POST",
		type: "POST",
		cache: false,
		data: formData,
		processData: false,
		contentType: false,
	}).then(function(response) {
		console.log("Card saved")
	});
}

/**
 * Ping the imported card to exchange the secret for credentials.
 *
 * @return	{object} The ping response.
 */
function ping() {
	console.log("Pinging card");
	var access_token = decodeURIComponent(getCookie("access_token"));
	access_token = access_token.substring(2, access_token.indexOf("."));
	return jQuery.ajax({
		url: `${host}:${hyperldger_port}/api/system/ping`,
		method: "GET",
		type: "GET",
		headers: {
			"X-Access-Token": access_token,
		},
	});
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
* Get the value of the cookie having the given name.
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
