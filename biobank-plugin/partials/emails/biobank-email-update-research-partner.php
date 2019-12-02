<html>
	<body>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-header.php"); ?>
		<p>Your Dwarna password has been updated. Keep it safe and use it to log in to Dwarna.</p>
		<p>New password: <?= $input['password'] ?></p>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-footer.php"); ?>
	</body>
</html>
