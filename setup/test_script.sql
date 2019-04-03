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
