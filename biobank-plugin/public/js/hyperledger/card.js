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
 * The logged-in user's username.
 */

/**
* When the document loads, check import the user's card.
*/
jQuery(document).ready(function(){
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
});

/**
 * Load the user's card if they have one.
 * This card allows them to make requests to the Hyperledger API.
 */
function loadCard() {
	jQuery.get(`${ajax_base_path}has_card.php?temp=false`).then(function(response) {
		/*
		 * If the user has a credential card, load it.
		 * Otherwise, import the temporary card.
		 */
		var access_token = decodeURIComponent(getCookie(hyperledger_access_token));
		access_token = access_token.substring(2, access_token.indexOf("."));
		if (response) {
 			console.log("Getting credentials card");
 			importCard(false);
		} else {
			tryImport(access_token);
 		}
	});
}

/**
 * When a card is found, load it and import it into the authenticated user's wallet.
 *
 * @param	{boolean} temp - A boolean indicating whether the temporary or credentials card is being loaded.
 */
function importCard(temp) {
	var request = new XMLHttpRequest();
	var access_token = decodeURIComponent(getCookie("access_token"));
	access_token = access_token.substring(2, access_token.indexOf("."));
	/*
	 * Get the card from the backend.
	 */
	request.open("GET", `${ajax_base_path}get_card.php?temp=${temp ? "true" : "false"}`, true);
	request.onreadystatechange = function(){
		if(this.readyState == 4) {
			if(this.status == 200) {
				var blob = new Blob([this.response], {type: "application/octet-stream"});
				var cardData = blob;
				const file = new File(
					[cardData], "card.card",
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
					if (temp) {
						jQuery.ajax({
							url: `${host}:${hyperldger_port}/api/system/ping`,
							method: "GET",
							type: "GET",
							headers: {
								"X-Access-Token": access_token,
							},
						}).then(function(response) {
							console.log("System pinged");
							exportCard(access_token);
						});
					}
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
 * Check whether the user has imported a card already.
 *
 * @param	{string} access_token - The user's Hyperledger access token.
 *									This token is stored as a cookie.
 *
 * @return	{mixed} The cookie's value, or null if no cookie with the given name is found.
 */
function tryImport(access_token) {
	var request = new XMLHttpRequest();
	request.open("GET", `${host}:${hyperldger_port}/api/wallet/card`, true);
	request.setRequestHeader("X-Access-Token", access_token);
	request.onreadystatechange = function() {
		if(this.readyState == 4) {
			if (this.status == 200) {
				console.log("Getting imported card");
				exportCard(access_token);
			} else {
				console.log("Getting temporary card");
				importCard(true);
			}
		}
	}
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

				saveCard(card);
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
* Get the value of the cookie having the given name.
* Based on https://stackoverflow.com/a/1599291/1771724
*
* @param	{string} name - The name of the cookie whose value to retrieve.
*
* @return	{mixed} The cookie's value, or null if no cookie with the given name is found.
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
