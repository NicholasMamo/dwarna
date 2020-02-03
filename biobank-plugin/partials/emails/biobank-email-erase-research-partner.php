<html>
	<body>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-header.php"); ?>
		<p>This is to confirm that user <?= $user->data->user_login ?> has requested that their data is removed and that their biospecimen is destroyed.</p>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-footer.php"); ?>
	</body>
</html>
