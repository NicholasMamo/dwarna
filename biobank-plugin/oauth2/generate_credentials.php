<?php

/**
 * Generate a random string having the given length.
 * The generated string is made up of numbers and lowercase letters.
 *
 * From: https://stackoverflow.com/a/12570458/1771724
 *
 * @since	1.0.0
 * @param	int		$length	The length of the generated string.
 * @return	string	The generated string.
 */
function RandomString($length) {
    $keys = array_merge(range(0,9), range('a', 'z'));

    $key = "";
    for($i=0; $i < $length; $i++) {
        $key .= $keys[random_int(0, count($keys) - 1)];
    }
    return $key;
}

echo "Client ID:\t" . RandomString(32) . "\n";
echo "Client secret:\t" . RandomString(32) . "\n";

?>
