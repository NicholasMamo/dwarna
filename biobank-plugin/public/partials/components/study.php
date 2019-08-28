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
				<?= $consent == 1 ? "Give to" : "Withdraw from" ?> <?= $studies->data->$study_id->study->name ?>
			</li>
	<?php
		}
	?>
		</ul>
	</li>
<?php } ?>
</ul>

<form class="<?= $this->plugin_name ?>-form" id="consent-form-<?= $study->study->study_id ?>"
	  method="post" name="consent_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<h4><?= $study->study->name ?></h4>
	<input type="hidden" name="action" value="consent_form">
	<?php wp_nonce_field("consent_form", "consent_nonce"); ?>

	<p class="biobank-description"><?= $study->study->description ?></p>
	<p class="biobank-homepage"><a href="<?= $study->study->homepage ?>" target="_blank">Read more</a></p>
	<div class='row'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>">Participate</label>
		</div>
		<div class='col-md-7'>
			<input id='<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-address'
				   name='<?= $this->plugin_name ?>[address]'
				   type='hidden' value=''>
			<input name='<?= $this->plugin_name ?>[study][study_id]'
				   type='hidden' value='<?= $study->study->study_id ?>'>
			<input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>'
				   name = '<?= $this->plugin_name ?>[study][consent]'
				   class = 'study-consent'
				   type = 'checkbox'>
		</div>
	</div>
	<div class='row'>
		<div class='col-md-7 offset-md-5'>
			<input type = "submit" class = "btn btn-primary float-left" />
		</div>
	</div>
</form>
