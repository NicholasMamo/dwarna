#!/usr/bin/env python3
"""
Create the schema for the biobank.
"""

import os
from os.path import expanduser

import psycopg2

"""
The database used by default
"""
DEFAULT_DATABASE = "biobank"

def create_schema(database):
	"""
	Create the schema in the given database.
	It is assumed that the database exists.
	This function can be used to create a test environment, refreshing the schema in just one database.
	"""
	try:
		# get the connection details from the .pgpass file
		home = expanduser("~")
		with open(os.path.join(home, ".pgpass"), "r") as f:
			# TODO: Uses the credentials from only the first line.
			host, port, _, username, password = f.readline().strip().split(":")
			# establish a connection
			con = psycopg2.connect(dbname=database, user=username, host=host, password=password)
			# create a psycopg2 cursor that can execute queries
			cursor = con.cursor()

			"""
			Create the users' tables.
			"""

			# drop the user roles if they exist
			cursor.execute("""DROP TYPE IF EXISTS user_role CASCADE""")
			cursor.execute("""CREATE TYPE user_role AS ENUM ('BIOBANKER', 'RESEARCHER', 'PARTICIPANT')""")

			# drop the user table if it exists
			cursor.execute("""DROP TABLE IF EXISTS users CASCADE;""")
			# create a new table with the most basic and required user fields
			cursor.execute("""CREATE TABLE users (
								user_id 			VARCHAR(64)		PRIMARY KEY,
								role				user_role
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN users.user_id IS 'The user''s unique identifier - a username or a pseudo-ID';""")
			cursor.execute("""COMMENT ON COLUMN users.role IS 'The user''s role';""")

			"""
			Create the specific user role tables.
			This follows generalization specialization relational modeling (http://www.javaguicodexample.com/erdrelationalmodelnotes1.html).
			The biobanker does not require any additional fields.
			The participant does not require any additional fields.
			"""

			# drop the researcher table if it exists
			cursor.execute("""DROP TABLE IF EXISTS researchers CASCADE;""")
			"""
			Create the researchers table.
			When a user is deleted, their corresponding researcher-specific data should also be removed.
			"""
			cursor.execute("""CREATE TABLE researchers (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN researchers.user_id IS 'The researcher''s unique identifier, links to the ''users'' table''s primary key';""")

			# drop the participants table if it exists
			cursor.execute("""DROP TABLE IF EXISTS participants CASCADE;""")
			"""
			Create the participants table.
			When a user is deleted, their corresponding participant-specific data should also be removed.
			"""
			cursor.execute("""CREATE TABLE participants (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE,
								name				VARCHAR(256),
								email				VARCHAR(256)
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN participants.user_id IS 'The participant''s unique identifier, links to the ''users'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN participants.name IS 'The participant''s name';""")
			cursor.execute("""COMMENT ON COLUMN participants.user_id IS 'The participant''s email address';""")

			# drop the biobankers table if it exists
			cursor.execute("""DROP TABLE IF EXISTS biobankers CASCADE;""")
			"""
			Create the biobankers table.
			When a user is deleted, their corresponding biobanker-specific data should also be removed.
			"""
			cursor.execute("""CREATE TABLE biobankers (
								user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN biobankers.user_id IS 'The biobanker''s unique identifier, links to the ''users'' table''s primary key';""")

			"""
			Create the studies' table.
			"""

			cursor.execute("""DROP TABLE IF EXISTS studies CASCADE;""")
			cursor.execute("""CREATE TABLE studies (
								study_id			VARCHAR(128)		PRIMARY KEY,
								name				VARCHAR(256),
								description			VARCHAR(1024),
								homepage			VARCHAR(512)
			);""")
			cursor.execute("""COMMENT ON COLUMN studies.study_id IS 'The study''s unique identifier';""")
			cursor.execute("""COMMENT ON COLUMN studies.name IS 'The study''s name';""")
			cursor.execute("""COMMENT ON COLUMN studies.description IS 'A description of what the study is about';""")
			cursor.execute("""COMMENT ON COLUMN studies.homepage IS 'A URL from where participants can obtain more information about the study';""")

			"""
			Create the relation table joining researchers with studies.
			A researcher may only view studies in which they are participating.
			"""

			cursor.execute("""DROP TABLE IF EXISTS studies_researchers;""")
			cursor.execute("""CREATE TABLE studies_researchers (
								study_id			VARCHAR(128)	REFERENCES studies(study_id) ON DELETE CASCADE,
								researcher_id		VARCHAR(64)		REFERENCES researchers(user_id) ON DELETE CASCADE
			);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN studies_researchers.study_id IS 'The study''s unique identifier, links to the ''studies'' table''s primary key';""")
			cursor.execute("""COMMENT ON COLUMN studies_researchers.researcher_id IS 'The researcher''s unique identifier, links to the ''researchers'' table''s primary key';""")

			"""
			When a user is removed from the users table, the deletion effect cascades.
			However, the inverse is not true.
			This trigger removes a user from the users table when the user is removed from a more specific table (participants, biobankers, researchers).
			"""
			cursor.execute("""
				CREATE OR REPLACE FUNCTION remove_from_users() RETURNS trigger AS
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

			con.commit() # commit the changes
	except Exception as e:
		print(e)

if __name__ == "__main__":
	create_schema(DEFAULT_DATABASE)
