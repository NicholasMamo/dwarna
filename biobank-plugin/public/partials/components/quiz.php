<div id ='quiz'>
	<?php foreach ($quiz as $i => $question) { ?>
	<div class='question'>
		<div class='row mx-1'><?= $question->question ?></div>
		<div class='row explanation'><?= $question->explanation ?></div>
		<input type='hidden' value='<?= $question->answer ?>'>
		<div class='row mx-3 mb-2'>
			<div class='col-md-6 text-center'>
				<input id="biobank-question-<?= $i ?>-yes" class='radio' value='yes' type='radio'>
				<label for="biobank-question-<?= $i ?>-yes">Yes</label>
			</div>
			<div class='col-md-6 text-center'>
				<input id="biobank-question-<?= $i ?>-no" class='radio' value='no' type='radio'>
				<label for="biobank-question-<?= $i ?>-no">No</label>
			</div>
		</div>
	</div>
	<?php } ?>
</div>
