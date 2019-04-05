/**
 * Parse the WordPress profile.
 * The function accepts both a parsed object and a JSON string.
 *
 * The function returns a user profile object that contains:
 *	- The user ID;
 *	- The user's display name;
 *	- The user's unique username; and
 *	- Optionally, if availabe, the user's email.
 *
 * Example input:
 * { ID: '1',
 *		user_login: 'nicholas',
 *		user_pass: '$P$BJTBqvJ4/KAz/H9nBzIxAJA3rnKpUI1',
 *		user_nicename: 'nicholas',
 *		user_email: 'nicholas.mamo@um.edu.mt',
 *		user_url: '',
 *		user_registered: '2018-08-01 08:34:32',
 *		user_activation_key: '',
 *		user_status: '0',
 *		display_name: 'nicholas' }
 *
 * @param {object|string} json
 * @return {object}
 * @access public
 */
exports.parse = function(json) {
	if ('string' == typeof json) {
		json = JSON.parse(json);
	}

	var profile = {};
	profile.id = String(json.ID);
	profile.displayName = json.display_name;
	profile.username = json.user_login;
	if (json.user_email) {
		profile.user_emails = [{ value: json.user_email }];
	}

	return profile;
};
