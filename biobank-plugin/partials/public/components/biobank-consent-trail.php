<h2>Consent trail</h2>
<div id='<?= $this->plugin_name ?>-consent-trail'>
	<div class='<?= $this->plugin_name ?>-wrapper'>
		<?php foreach ($timeline as $timestamp => $changes) { ?>
		<div class='<?= $this->plugin_name ?>-node'>
			<div class='<?= $this->plugin_name ?>-datetime'>
				<div class='<?= $this->plugin_name ?>-date'><?= DateTime::createFromFormat("U", $timestamp)->format("j M Y") ?></div>
				<div class='<?= $this->plugin_name ?>-time'><?= DateTime::createFromFormat("U", $timestamp)->format("H:i") ?></div>
			</div>
			<?php foreach ((array) $changes as $study_id => $consent) { ?>
					<?php if ($study_id == $study->study->study_id) { ?>
					<div class='<?= $this->plugin_name ?>-consent-change'>
						<span>You <?= $consent == 1 ? "gave" : "withdrew" ?> consent</span>
					</div>
					<?php } ?>
			<?php } ?>
		</div>
		<?php } ?>
	</div>
</div>
