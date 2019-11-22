<?php

require_once(plugin_dir_path(__FILE__) . "../ui/fields.php");
require_once(plugin_dir_path(__FILE__) . "../../client/form/consent_form_handler.php");

$error = "";
$consent_handler = new \client\form\ConsentFormHandler();

$trail = $consent_handler->get_consent_trail();
$error = isset($trail->error) && ! empty($trail->error) ? $trail->error : $error;

$studies = (array) $trail->studies;
$timeline = (array) $trail->timeline;
ksort($timeline);

?>
<div class='biobank-consent'>

	<?php
	if (isset($error) && ! empty($error)) {
	?>
	<div class="error">
		<?= $error ?>
	</div>
	<?php
	}
	?>

	<ul>
	<?php
	foreach ($timeline as $timestamp => $changes) {
	?>
		<li><?= DateTime::createFromFormat("U", $timestamp)->format("jS M Y \a\\t H:i") ?>
			<ul>
		<?php
			$changes = (array) $changes;
			foreach ($changes as $study_id => $consent) {
		?>
				<li>
					<?= $consent == 1 ? "Give to" : "Withdraw from" ?> <?= $studies[$study_id]->name ?>
				</li>
		<?php
			}
		?>
			</ul>
		</li>
	<?php } ?>
	</ul>

</div>
