cursor.execute("""CREATE OR REPLACE FUNCTION add_user_by_role() RETURNS trigger AS
	$$BEGIN
		IF NEW.role = 'PARTICIPANT' THEN
			INSERT INTO "participants" (
				user_id)
			VALUES (NEW.user_id);
		END IF ;
		RETURN NEW ;
	END;$$
	LANGUAGE plpgsql;

	CREATE TRIGGER remove_user
		AFTER INSERT ON users FOR EACH ROW
		EXECUTE PROCEDURE add_user_by_role();""")
