<div id ='biobank-quiz'>
	<?php foreach ($quiz as $i => $question) { ?>
	<div class='biobank-question'>
		<div class='biobank-quiz-question'><?= $question->question ?></div>
		<div class='biobank-quiz-question-explanation'><?= $question->explanation ?></div>
		<input type='hidden' value='<?= $question->answer ?>'>
		<label class='radio-container'
			   for="biobank-question-<?= $i ?>-yes">Yes
			<input id="biobank-question-<?= $i ?>-yes" class='radio'
				   name="biobank-question-<?= $i ?>" value='yes' type='radio'>
			<span class='radio'></span>
		</label>
		<label class='radio-container'
			   for="biobank-question-<?= $i ?>-no">No
			<input id="biobank-question-<?= $i ?>-no" class='radio'
				   name="biobank-question-<?= $i ?>" value='no' type='radio'>
			<span class='radio'></span>
		</label>
	</div>
	<?php } ?>
</div>
