<?php

/**
 * A file that prints the data that it receives.
 */

header("Content-type: text/*");

session_start();

echo "Cookie\n";
var_dump($_COOKIE);

echo "\n";
echo "Session\n";
var_dump($_SESSION);

echo "\n";
echo "GET\n";
var_dump($_GET);

echo "\n";
echo "POST\n";
var_dump($_POST);

echo "\n";
echo "Server\n";
var_dump($_SERVER);

?>
