<div id='biobank-consent-trail'>
	<h2>Consent trail</h2>

	<ul>
	<?php
	foreach (array_reverse($timeline) as $timestamp => $changes) {
	?>
		<li><?= DateTime::createFromFormat("U", $timestamp)->format("jS M Y \a\\t H:i") ?>
			<ul>
		<?php
			foreach ((array) $changes as $study_id => $consent) {
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
