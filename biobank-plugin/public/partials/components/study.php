<h4><?= $study->study->name ?></h4>
<p class="biobank-description"><?= $study->study->description ?></p>
<p class="biobank-homepage"><a href="<?= $study->study->homepage ?>" target="_blank">Read more</a></p>
<table class="form-table">
<!-- <?php
foreach ($study->attributes as $attribute) {
	$field = \fields\create_form_field($this->plugin_name, $study->study->study_id, $attribute, $defaults);
?>
	<tr class="form-field form-required">
		<th scope="row">
			<label for="<?= $attribute->attribute_id ?>"><?= $attribute->name ?></label>
		</th>
		<td>
			<?= $field ?>
		</td>
	</tr>
<?php } ?> -->
	<tr class="form-field form-required">
		<th scope="row">
			<label for="<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>">Participate</label>
		</th>
		<td>
			<input name='<?= $this->plugin_name ?>[study][<?= $study->study->study_id ?>][consent]' type='hidden' value='0'>
			<input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>' name = '<?= $this->plugin_name ?>[study][<?= $study->study->study_id ?>][consent]' type = 'checkbox' <?= $consent === True ? "checked" : "" ?>>
		</td>
	</tr>
</table>
