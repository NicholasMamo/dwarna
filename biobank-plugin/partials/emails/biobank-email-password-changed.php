<html>
	<body>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-header.php"); ?>
		<p>Your Dwarna password has been changed and you can use it to log in to <?= get_bloginfo('name') ?> at <?= get_site_url() ?>.</p>
		<p>If this wasn't you, get in touch with us.</p>
		<?php include(plugin_dir_path(__FILE__) . "/biobank-email-footer.php"); ?>
	</body>
</html>
