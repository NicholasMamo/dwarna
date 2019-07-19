/**
 * A passport strategy, based on the OAuth 2.0 Authorization Code workflow.
 * The passport strategy is meant to be used with a local WordPress installation.
 *
 * The main diversion from the standard OAuth 2.0 is the way it parses profiles.
 * The strategy inherits most of the logic.
 */

// Load modules.
var OAuth2Strategy = require('passport-oauth2')
	, util = require('util')
	, Profile = require('./profile')
	, InternalOAuthError = require('passport-oauth2').InternalOAuthError
	, APIError = require('./errors/apierror');

/**
 * `Strategy` constructor.
 *
 * The local WordPress strategy authenticates users using a local WordPress installation.
 *
 * The specifics of how this authentication works is up to the CMS.
 * However, it is assumed that the Authorization Code flow is used.
 *
 * The local-wordpress passport is based on the passport-github implementation.
 * passport-github on GitHub: https://github.com/jaredhanson/passport-github
 * The passports are based on the OAuth 2.0 flow.
 *
 * Required options:
 *	- `clientID`			The application's Client ID.
 *	- `clientSecret`		The application's Client Secret.
 *	- `callbackURL`	 		The URL to which WordPress will redirect after granting authorization.
 *	- `authorizationURL`	The WordPress URL where the user grants authorization.
 *	- `tokenURL`			The WordPress URL where the application fetches the access token.
 *	- `userProfileURL`		The WordPress URL where the application fetches the user's profile.
 *
 * Optional options:
 *	- `state`				The application state, which may be required by WordPress.
 *							If not provided, a default one is used.
 *	- `scope`				Array of permission scopes to request.
 *							Available scopes depend on the WordPress API.
 *							If none are requested, a basic scope is usually given by the API.
 *	- `scopeSeparator`		The scope separator to use.
 *	- `userAgent`		 	All API requests MUST include a valid User Agent string.
 *							This could be the domain name of the application.
 *							If none is given, the request is made on behalf of the passport.
 *	- `customHeaders`		Any other headers that the passport should include in requests.
 *
 * @constructor
 * @param {object} options
 * @param {function} verify
 * @access public
 */
function Strategy(options, verify) {
	options = options || {};
	this._userProfileURL = options.userProfileURL;

	options.scopeSeparator = options.scopeSeparator || ',';
	options.customHeaders = options.customHeaders || {};
	options.state = options.state || "xyz";

	if (!options.customHeaders['User-Agent']) {
		options.customHeaders['User-Agent'] = options.userAgent || 'passport-local-wordpress';
	}

	/*
	 * Call the OAuth2Strategy function.
	 * This function uses the options and verify method to set instance variables.
	 * The instance variables that it sets are accessible from this function.
	 * Instance variables can be accessed using `this.var`.
	 *
	 * The name of the strategy is overriden to be more specific.
	 */
	 OAuth2Strategy.call(this, options, verify);
	 this.name = 'passport-local-wordpress';
	 this._oauth2.useAuthorizationHeaderforGET(true);

}

util.inherits(Strategy, OAuth2Strategy); // Inherit from `OAuth2Strategy`.

/**
 * Get the user's profile from the local WordPress installation.
 *
 * The profile is important to differentiate between users of the application.
 * The function uses the profile URL specified in the constructor.
 * It sends the access token to the WordPress installation to identify users.
 *
 * The function expects the returned user profile in JSON format.
 *
 * @param {string} accessToken
 * @param {function} done
 * @access public
 */
Strategy.prototype.userProfile = function(accessToken, done) {
	var self = this;

	/*
	 * The function makes a GET request to the user profile endpoint.
	 * It sends along the access token, which is used to authenticate users.
	 * The response is made up of:
	 *  - `error` 	An error, or null in the absence of any problems.
	 *	- `body`	The JSON response body.
	 *  - `res`		The full response.
	 */
	this._oauth2.get(self._userProfileURL, accessToken, function (err, body, res) {
		var json;

		/*
		 * Handle any initial errors in the response.
		 */
		if (err) {
			if (err.data) {
				try {
					json = JSON.parse(err.data);
				} catch (_) {}
			}

			if (json && json.message) {
				return done(new APIError(json.message));
			}
			return done(new InternalOAuthError('Failed to fetch user profile', err));
		}

		/*
		 * Parse the JSON string of the user profile.
		 */
		try {
			json = JSON.parse(body);
		} catch (ex) {
			return done(new Error('Failed to parse user profile'));
		}

		/*
		 * Create an actual user profile using the data in the response.
		 */
		var profile = Profile.parse(json);
		profile.provider = 'wordpress';
		profile._raw = body;
		profile._json = json;

		done(null, profile); // Return control to the next step of the process with the user profile.
	});
}

module.exports = Strategy; // Expose constructor.
