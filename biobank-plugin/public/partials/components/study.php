<h4><?= $study->study->name ?></h4>
<p class="biobank-description"><?= $study->study->description ?></p>
<p class="biobank-homepage"><a href="<?= $study->study->homepage ?>" target="_blank">Read more</a></p>
<table class="form-table">
	<tr class="form-field form-required">
		<th scope="row">
			<label for="<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>">Participate</label>
		</th>
		<td>
			<form class="<?= $this->plugin_name ?>-form" id="consent_form" method="post" name="consent_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
				<input type="hidden" name="action" value="consent_form">
				<?php wp_nonce_field("consent_form", "consent_nonce"); ?>

				<input name='<?= $this->plugin_name ?>[study][<?= $study->study->study_id ?>][consent]' type='hidden' value='0'>
				<input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>' name = '<?= $this->plugin_name ?>[study][<?= $study->study->study_id ?>][consent]' type = 'checkbox' <?= $consent === True ? "checked" : "" ?>>

				<input type = "submit" class = "primary" />
			</form>
		</td>
	</tr>
</table>
