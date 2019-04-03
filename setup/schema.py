"""
Create the schema
"""

from os.path import expanduser

import os
import psycopg2

"""
The database used by default
"""
DEFAULT_DATABASE = "tutorial"

def create_schema(database):
	"""
	Create the schema in the given database
	It is assumed that the database exists
	This function can be used to create a test environment, refreshing the schema in just one database
	"""
	try:
		# get the connection details from the .pgpass file
		home = expanduser("~")
		with open(os.path.join(home, ".pgpass"), "r") as f:
			host, port, _, username, password = f.readline().strip().split(":")
			# establish a connection
			con = psycopg2.connect(dbname=database, user=username, host=host, password=password)
			# create a psycopg2 cursor that can execute queries
			cursor = con.cursor()

			"""
			Create the users' tables
			"""

			# drop the user roles if they exist
			cursor.execute("""DROP TYPE IF EXISTS user_role CASCADE""")
			cursor.execute("""CREATE TYPE user_role AS ENUM ('BIOBANKER', 'RESEARCHER', 'PARTICIPANT')""")

			# drop the user table if it exists
			cursor.execute("""DROP TABLE IF EXISTS users CASCADE;""")
			# create a new table with the most basic and required user fields
			cursor.execute("""CREATE TABLE users (
								user_id 			VARCHAR(64)		PRIMARY KEY,
								email				VARCHAR(64)		NOT NULL,
								first_name			VARCHAR(32)		NOT NULL,
								last_name			VARCHAR(32)		NOT NULL,
								role				user_role
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN users.user_id IS 'The user''s unique identifier - a username or a pseudo-ID';""")
			cursor.execute("""COMMENT ON COLUMN users.email IS 'The user''s email address, used for correspondence';""")
			cursor.execute("""COMMENT ON COLUMN users.first_name IS 'The user''s first name';""")
			cursor.execute("""COMMENT ON COLUMN users.last_name IS 'The user''s last name';""")
			cursor.execute("""COMMENT ON COLUMN users.role IS 'The user''s role';""")

			"""
			Create the specific user role tables
			This follows generalization specialization relational modeling (http://www.javaguicodexample.com/erdrelationalmodelnotes1.html)
			The biobanker does not require any additional fields
			The participant does not require any additional fields
			"""

			# drop the researcher table if it exists
			cursor.execute("""DROP TABLE IF EXISTS researchers CASCADE;""")
			"""
			Create the researchers table
			When a user is deleted, their corresponding researcher-specific data should also be removed
			"""
			cursor.execute("""CREATE TABLE researchers (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE,
								affiliation			VARCHAR(128) 	DEFAULT '',
								role				VARCHAR(128) 	DEFAULT ''
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN researchers.user_id IS 'The researcher''s unique identifier, links to the ''users'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN researchers.affiliation IS 'The researcher''s affiliated institution';""")
			cursor.execute("""COMMENT ON COLUMN researchers.role IS 'The researcher''s role within the project';""")

			# drop the participants table if it exists
			cursor.execute("""DROP TABLE IF EXISTS participants CASCADE;""")
			"""
			Create the participants table
			When a user is deleted, their corresponding participant-specific data should also be removed
			"""
			cursor.execute("""CREATE TABLE participants (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN participants.user_id IS 'The participant''s unique identifier, links to the ''users'' table''s primary key';""")

			# drop the biobankers table if it exists
			cursor.execute("""DROP TABLE IF EXISTS biobankers CASCADE;""")
			"""
			Create the biobankers table
			When a user is deleted, their corresponding biobanker-specific data should also be removed
			"""
			cursor.execute("""CREATE TABLE biobankers (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN biobankers.user_id IS 'The biobanker''s unique identifier, links to the ''users'' table''s primary key';""")

			"""
			Create the studies' table
			"""

			cursor.execute("""DROP TABLE IF EXISTS studies CASCADE;""")
			cursor.execute("""CREATE TABLE studies (
								study_id			SERIAL PRIMARY KEY,
								name				VARCHAR(256),
								description			VARCHAR(1024),
								homepage			VARCHAR(512),
								start_date			DATE,
								end_date			DATE
			);""")
			cursor.execute("""COMMENT ON COLUMN studies.study_id IS 'The study''s unique identifier';""")
			cursor.execute("""COMMENT ON COLUMN studies.name IS 'The study''s name';""")
			cursor.execute("""COMMENT ON COLUMN studies.description IS 'A description of what the study is about';""")
			cursor.execute("""COMMENT ON COLUMN studies.homepage IS 'A URL from where participants can obtain more information about the study';""")
			cursor.execute("""COMMENT ON COLUMN studies.start_date IS 'The date when the study is scheduled to start';""")
			cursor.execute("""COMMENT ON COLUMN studies.end_date IS 'The date when the study is scheduled to end';""")

			"""
			Create the relation table joining participants with studies
			This is the Dynamic Consent component of the schema
			"""

			cursor.execute("""DROP TABLE IF EXISTS studies_participants;""")
			cursor.execute("""CREATE TABLE studies_participants (
								study_id			INT				REFERENCES studies(study_id) ON DELETE CASCADE,
								participant_id		VARCHAR(64)		REFERENCES participants(user_id) ON DELETE CASCADE,
								consent				BOOLEAN			DEFAULT FALSE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN studies_participants.study_id IS 'The study''s unique identifier, links to the ''studies'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN studies_participants.participant_id IS 'The participant''s unique identifier, links to the ''participants'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN studies_participants.consent IS 'A boolean flag indicating whether the participant has given consent (true) or not (false)';""")

			"""
			Add study attributes
			The primary key of attributes is composite, made of the name and type
			This allows attributes to be shared between studies, so that participants do not have to manually re-input attributes
			"""

			# clear the attribute types if they exist
			cursor.execute("""DROP TYPE IF EXISTS attribute_type CASCADE""")
			cursor.execute("""CREATE TYPE attribute_type AS ENUM ('BOOLEAN', 'INTEGER', 'REAL', 'ENUMERATION', 'STRING')""")

			cursor.execute("""DROP TABLE IF EXISTS attributes CASCADE;""")
			"""
			The table checks that if an enumeration is provided, possibilities are also given
			"""
			cursor.execute("""CREATE TABLE attributes(
								name				VARCHAR(128) 	NOT NULL,
								type				attribute_type	NOT NULL,
								constraints			TEXT []			DEFAULT '{}',
								CONSTRAINT  valid_enumeration_possibilities CHECK (type <> 'ENUMERATION' OR COALESCE(ARRAY_LENGTH(constraints, 1), 0) <> 0),
								PRIMARY KEY (name, type)
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN attributes.name IS 'The display name of the attribute';""")
			cursor.execute("""COMMENT ON COLUMN attributes.type IS 'The data type of the attribute, one of a pre-defined enumeration';""")
			cursor.execute("""COMMENT ON COLUMN attributes.constraints IS 'Constraints on the attribute - in many cases, this can be left empty, but if the type of the attribute is an enumeration, a list of possibilities should be given';""")

			"""
			Create the relation table joining participants with attributes
			The value of attributes is always a string of characters
			Values can be parsed according to their type
			"""

			cursor.execute("""DROP TABLE IF EXISTS participants_attributes;""")
			cursor.execute("""CREATE TABLE participants_attributes (
								participant_id		VARCHAR(64)		REFERENCES participants(user_id) ON DELETE CASCADE,
								attribute_name		VARCHAR(128)	NOT NULL,
								attribute_type		attribute_type	NOT NULL,
								value				VARCHAR(256)	NOT NULL,
								FOREIGN KEY (attribute_name, attribute_type) REFERENCES attributes(name, type) ON DELETE CASCADE,
								PRIMARY KEY (participant_id, attribute_name, attribute_type)
			);"""),

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN participants_attributes.participant_id IS 'The participant''s unique identifier, links to the ''participants'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants_attributes.attribute_name IS 'The display name of the attribute, links to the ''attributes'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants_attributes.attribute_type IS 'The type of the attribute, one of a pre-defined enumeration, links to the ''attributes'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants_attributes.value IS 'The participant''s value for the given attribute';""")

			"""
			Create the relation table joining studies with attributes
			This is necessary because the schema allows a study to have multiple attributes, and for attributes to be shared between studies
			"""

			cursor.execute("""DROP TABLE IF EXISTS studies_attributes;""")
			cursor.execute("""CREATE TABLE studies_attributes (
								study_id			INT				REFERENCES studies(study_id) ON DELETE CASCADE,
								attribute_name		VARCHAR(128)	NOT NULL,
								attribute_type		attribute_type	NOT NULL,
								FOREIGN KEY (attribute_name, attribute_type) REFERENCES attributes(name, type) ON DELETE CASCADE,
								PRIMARY KEY (study_id, attribute_name, attribute_type)
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN studies_attributes.study_id IS 'The study''s unique identifier, links to the ''studies'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants_attributes.attribute_name IS 'The display name of the attribute, links to the ''attributes'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants_attributes.attribute_type IS 'The type of the attribute, one of a pre-defined enumeration, links to the ''attributes'' table''s primary key';""")

			"""
			When a user is removed from the users table, the deletion effect cascades
			However, the inverse is not true
			This trigger removes a user from the users table when the user is removed from a more specific table (participants, biobankers, researchers)
			"""
			cursor.execute("""CREATE OR REPLACE FUNCTION remove_from_users() RETURNS trigger AS
				$$BEGIN
		   			DELETE FROM "users"
			  			WHERE user_id = OLD.user_id;
		  			RETURN OLD;
				END;$$
				LANGUAGE plpgsql;

				CREATE TRIGGER remove_participant
		   			AFTER DELETE ON participants FOR EACH ROW
		   			EXECUTE PROCEDURE remove_from_users();

				CREATE TRIGGER remove_biobanker
		   			AFTER DELETE ON biobankers FOR EACH ROW
		   			EXECUTE PROCEDURE remove_from_users();

				CREATE TRIGGER remove_researcher
		   			AFTER DELETE ON researchers FOR EACH ROW
		   			EXECUTE PROCEDURE remove_from_users();""")

			# commit the changes
			con.commit()
	except Exception as e:
		print(e)

if __name__ == "__main__":
	create_schema(DEFAULT_DATABASE)
