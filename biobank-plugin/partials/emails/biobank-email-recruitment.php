<html>
	<body>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-header.php"); ?>
		<p>New Research Partner: <?= $input['name'] ?></p>
		<p>Mobile: <?= $input['mobile'] ?></p>
		<p>Email: <?= $input['email'] ?></p>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-footer.php"); ?>
	</body>
</html>
