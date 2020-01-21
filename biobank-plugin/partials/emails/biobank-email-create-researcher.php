<html>
	<body>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-header.php"); ?>
		<p>Your new Dwarna account is ready to be used. Keep your password safe and use it to log in to Dwarna.</p>
		<p>Username: <?= $input['username'] ?></p>
		<p>Password: <?= $input['password'] ?></p>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-footer.php"); ?>
	</body>
</html>
