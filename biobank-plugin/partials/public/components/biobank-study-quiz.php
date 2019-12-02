<div id ='biobank-quiz'>
	<?php foreach ($quiz as $i => $question) { ?>
	<div class='biobank-question'>
		<div class='biobank-quiz-question'><?= $question->question ?></div>
		<div class='biobank-quiz-question-explanation'><?= $question->explanation ?></div>
		<input type='hidden' value='<?= $question->answer ?>'>
		<input id="biobank-question-<?= $i ?>-yes" class='radio'
			   name="biobank-question-<?= $i ?>" value='yes' type='radio'>
		<label for="biobank-question-<?= $i ?>-yes">Yes</label>
		<input id="biobank-question-<?= $i ?>-no" class='radio'
			   name="biobank-question-<?= $i ?>" value='no' type='radio'>
		<label for="biobank-question-<?= $i ?>-no">No</label>
	</div>
	<?php } ?>
</div>
