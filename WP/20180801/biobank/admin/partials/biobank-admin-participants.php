<?php

/**
 * Provide an area where biobankers can create, edit and remove participants
 *
 * @link       https://github.com/nmamo
 * @since      1.0.0
 *
 * @package    Biobank
 * @subpackage Biobank/admin/partials
 */

if (isset($_POST[$this->plugin_name])) {
    $edit = true;
} else {
    $edit = false;
}

$settings_group = $this->plugin_name . "-participants";
settings_errors($settings_group);

?>

<div class="wrap">
    <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
    <h2>Add, edit or remove biobank participants</h2>

    <form method="post" name="participant_form" action="#">
        <?php settings_fields($settings_group); ?>

        <fieldset>
            <legend class="screen-reader-text"><span>Username (required)</span></legend>
            <label for="<?php echo "participant"; ?>-username">
                <span><?php esc_attr_e('Username (required)', "participant"); ?></span>
                <input type="text" id="<?php echo "participant"; ?>-username" name="<?php echo "participant"; ?>[username]" value="" />
            </label>
        </fieldset>

        <?php submit_button(($edit ? "Update" : "Create") . " participant", 'primary','submit', TRUE); ?>
    </form>
</div>
