<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

//step1
$cSession = curl_init();
//step2
$access_token = "tx2D0x3NebT6nSFPkVBBB1ClXKSn5xdM9YeF6C5AjZV030KVdAdcDkOBLC1oqUBZ";
curl_setopt($cSession,CURLOPT_URL,"http://localhost:3000/api/wallet?access_token=$access_token");
curl_setopt($cSession,CURLOPT_RETURNTRANSFER,true);
curl_setopt($cSession,CURLOPT_HEADER, false);
//step3
$result=curl_exec($cSession);
//step4
curl_close($cSession);
//step5
var_dump($result);
?>
