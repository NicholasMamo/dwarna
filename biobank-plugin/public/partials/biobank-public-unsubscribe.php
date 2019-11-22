<form class="<?= $this->plugin_name ?>-form" id="unsubscribe-form"
	  method="post" name="unsubscribe_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="unsubscribe_form">
	<?php wp_nonce_field("unsubscribe_form", "unsubscribe_nonce"); ?>

	<div class='row my-2'>
		<div class='col-md-5 text-md-right'>
			<label for="<?= $this->plugin_name ?>-email">Email address</label>
		</div>
		<div class='col-md-5'>
			<input id='<?= $this->plugin_name ?>-email'
				   class='form-control'
				   name='<?= $this->plugin_name ?>[email]'
				   type='email' value='' placeholder="joe.borg@gmail.com">
		</div>
	</div>

	<div class='row my-2'>
		<div class='col-md-7 offset-md-5'>
			<input type = "submit" class = "btn btn-primary float-left" value="Unsubscribe" />
		</div>
	</div>
</form>
