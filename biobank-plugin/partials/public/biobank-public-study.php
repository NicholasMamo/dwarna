<?php
if (isset($error) && ! empty($error)) {
?>
<div class="error">
	<?= $error ?>
</div>
<?php
} else if (isset($_GET['return']) && $_GET['return'] = 'update_consent') {
?>
	<?php
		if (isset($_GET['withdraw']) && $_GET['withdraw'] == 'withdraw_consent') {
	?>
		<div class="<?= $this->plugin_name ?>-alert" style="background-color:#FABD41 !important">
		Your sample and data will no longer be used in this study, but will remain stored in the biobank for fut$
		If you would like to destroy your sample, or AMEND your original consent form please phone the biobank m$
		</div>
	<?php
		}
	?>

<div class="<?= $this->plugin_name ?>-alert">
	Consent update will be confirmed soon via email
</div>
<?php
}
?>

<input id='study-name' type='hidden' value="<?= htmlspecialchars($study->study->name) ?>" />

<form class="<?= $this->plugin_name ?>-form" id="consent-form-<?= $study->study->study_id ?>"
	  method="post" name="consent_form" action=<?php echo esc_url(admin_url("admin-post.php")); ?>>
	<input type="hidden" name="action" value="consent_form">
	<?php wp_nonce_field("consent_form", "consent_nonce"); ?>

	<!-- <p class="biobank-description"><?= $study->study->description ?> <span class="biobank-homepage"><a href="<?= $study->study->homepage ?>" target="_blank">Read more</a></span></p> -->
	
	<?php
		if (!(isset($_GET['return']) && $_GET['return'] = 'update_consent')) {
	?>
	<p class="biobank-description"><?= $study->study->description ?> <span class="biobank-homepage"></span></p>
	<?php
		}
	?>
	
	<?php if ($study->study->attachment != ''): ?>
		<iframe src="<?= $study->study->attachment ?>" width="100%" height="500px"></iframe>
	<?php endif; ?>
	

	<?php 
		require_once(plugin_dir_path(__FILE__) . "../../client/form/consent_form_handler.php");
		$consent_handler = new \client\form\ConsentFormHandler();
		if ($consent_handler->consented_to_study($study->study->study_id)) {
    ?>
    
	<?php
		if (!(isset($_GET['return']) && $_GET['return'] = 'update_consent')) {
	?>
        <p>I would like researchers to STOP using my banked sample and data for this research study.</p>
        
       <input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>'
	            name = '<?= $this->plugin_name ?>[study][consent]'
			    class = 'study-consent' 
			    type = 'hidden'>
			    
       <input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-consenting'
       		  name = '<?= $this->plugin_name ?>[study][consenting]'
		      class = 'study-consenting <?= $this->plugin_name ?>-hidden' 
		      type = 'hidden'>

	    <input name='<?= $this->plugin_name ?>[study][study_id]'
		       type='hidden' 
		       value='<?= $study->study->study_id ?>'>
		       
	    <input id='<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-address'
		       name='<?= $this->plugin_name ?>[address]'
		       type='hidden' 
		       value=''>

	    <input type = "submit" class = "btn btn-primary float-left" value="Withdraw Consent" />
		<?php
		}
	?>
    
	<?php } else { ?>
	
		<?php
		if (!(isset($_GET['return']) && $_GET['return'] = 'update_consent')) {
	?>
		<?php include_once(plugin_dir_path(__FILE__) . '/components/biobank-study-quiz.php') ?>

	    <h2>Consent Update</h2>
	    <div class="<?= $this->plugin_name ?>-alert <?= $this->plugin_name ?>-quiz-alert
				    <?= $this->plugin_name ?>-hidden">
		    Please fill in the quiz above before continuing.
	    </div>

	    <label class='checkbox-container'
		       for="<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>">
		       <span id='<?= $this->plugin_name ?>-consented' hidden>
			       I no longer wish to participate in this study
		       </span>
		       <span id='<?= $this->plugin_name ?>-not-consented' hidden>
			       I agree that my sample at the biobank can be used for this study
		       </span>

	       <input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>'
	       		  name = '<?= $this->plugin_name ?>[study][consent]'
			      class = 'study-consent' type = 'checkbox'>
	       <span class='checkbox'></span>
       </label>
       <input id = '<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-consenting'
       		  name = '<?= $this->plugin_name ?>[study][consenting]'
		      class = 'study-consenting <?= $this->plugin_name ?>-hidden' type = 'checkbox'>

	    <input name='<?= $this->plugin_name ?>[study][study_id]'
		       type='hidden' value='<?= $study->study->study_id ?>'>
	    <input id='<?= $this->plugin_name ?>-study-<?= $study->study->study_id ?>-address'
		       name='<?= $this->plugin_name ?>[address]'
		       type='hidden' value=''>

	    <input type = "submit" class = "btn btn-primary float-left" />
		<?php
		}
	?>
	
	<?php }	?>
	
</form>
<?php include_once(plugin_dir_path(__FILE__) . '/components/biobank-consent-trail.php') ?>
	

