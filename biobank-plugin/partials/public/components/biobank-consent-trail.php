<div id='biobank-consent-trail'>
	<h2>Consent trail</h2>

	<?php foreach ($timeline as $timestamp => $changes) { ?>
	<div class='<?= $this->plugin_name ?>-node'>
		<div class='<?= $this->plugin_name ?>-datetime'>
			<div class='<?= $this->plugin_name ?>-date'><?= DateTime::createFromFormat("U", $timestamp)->format("j M Y") ?></div>
			<div class='<?= $this->plugin_name ?>-time'><?= DateTime::createFromFormat("U", $timestamp)->format("H:i") ?></div>
		</div>
		<?php foreach ((array) $changes as $study_id => $consent) { ?>
				<?php if ($study_id == $study->study->study_id) { ?>
				<div class='<?= $this->plugin_name ?>-consent-change'><?= $consent == 1 ? "You gave consent" : "You withdrew consent" ?></div>
				<?php } ?>
		<?php } ?>
		<?php } ?>
	</div>
</div>
