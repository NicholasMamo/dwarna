<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

//step1
$cSession = curl_init();
//step2
curl_setopt($cSession,CURLOPT_URL,"http://localhost:3000/api/wallet/5%40collectable-penguin-network/export?access_token=9YBQBJtIapVNYmYYEtNqR0EPPO846nPHVL8uqxF7XeeCBQOiv0DxmPEHYUyoTboh");
curl_setopt($cSession,CURLOPT_RETURNTRANSFER,true);
curl_setopt($cSession,CURLOPT_HEADER, false);
//step3
$result=curl_exec($cSession);
//step4
curl_close($cSession);
//step5

file_put_contents("cards/5@collectable-penguin-network.card", $result);

?>
