(function( $ ) {
	'use strict';
})( jQuery );

/*
 * General script functions.
 */

/**
 * Get the full path to the script having the given name.
 *
 * @param	{DOM Element} script - The script element whose path will be extracted - usually fetched using document.currentScript.
 * @return	{string} The full path to the script having the given name. The path includes a trailing slash.
 */
function get_script_path(script) {
	var link = jQuery(script).attr("src"); // scripts have a `src` attribute
	if (typeof link !== typeof undefined) { // some scripts are inline, and thus have no source
		var script_dir = link.substr(0, link.lastIndexOf("/") + 1); // retain a trailing slash
		return script_dir;
    }

	return "";
}
