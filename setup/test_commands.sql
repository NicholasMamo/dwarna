DELETE FROM users WHERE TRUE;
DELETE FROM participants WHERE TRUE;
DELETE FROM participants_attributes WHERE TRUE;
DELETE FROM attributes WHERE TRUE;

INSERT INTO users (
			user_id, email, first_name, last_name, role)
			VALUES ('t_id', 't@ema.il', 'f', 'l', 'PARTICIPANT');
INSERT INTO participants (
			user_id)
			VALUES ('t_id');
INSERT INTO attributes(
			name, type)
			VALUES ('Smokes', 'BOOLEAN');
INSERT INTO participants_attributes(
			participant_id, attribute_name, attribute_type, value)
			VALUES ('t_id', 'Smokes', 'BOOLEAN', TRUE);

-- SELECT * FROM users;
-- SELECT * FROM participants;
-- SELECT * FROM participants_attributes;
-- SELECT * FROM attributes;

-- all user info should be gone, but attribute should still exist
DELETE FROM users WHERE user_id = 't_id';

-- all user and attribute info should be retained, but not the participant's attribute
DELETE FROM participants_attributes WHERE participant_id = 't_id';

-- all user info should be retained, but not the participant's attribute and the attribute itself
DELETE FROM attributes WHERE name = 'Smokes';
