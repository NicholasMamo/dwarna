<div id='biobank-consent-trail'>
	<h2>Consent trail</h2>

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
				<?php if ($study_id == $study->study->study_id) { ?>
				<li>
					<?= $consent == 1 ? "Give to" : "Withdraw from" ?> <?= $study->study->name ?>
				</li>
				<?php } ?>
		<?php
			}
		?>
			</ul>
		</li>
	<?php } ?>
	</ul>
</div>
