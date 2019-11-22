<form class="<?= $this->plugin_name ?>-form" id="subscription-form"
	  method="post" name="subscription_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="update_subscription">
	<?php wp_nonce_field("subscription_form", "subscription_nonce"); ?>

	<div class='row my-2'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-any">Any emails</label>
		</div>
		<div class='col-md-5'>
			<input id='<?= $this->plugin_name ?>-any'
				   name='<?= $this->plugin_name ?>[any_email]'
				   type='checkbox' <?= $subscriptions->data->any_email ? 'checked' : '' ?>>
		</div>
	</div>

	<div class='row my-2'>
		<div class='col-md-7 offset-md-5'>
			<input type = "submit" class = "btn btn-primary float-left" value="Update subscription" />
		</div>
	</div>
</form>