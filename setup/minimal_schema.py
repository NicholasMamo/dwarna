#!/usr/bin/env python3
"""
Create the schema for the biobank.
"""

import argparse
import os
from os.path import expanduser

import psycopg2
import sys

path = sys.path[0]
path = os.path.join(path, "..", "rest")
if path not in sys.path:
	sys.path.insert(1, path)

from connection.db_connection import PostgreSQLConnection

"""
The database used by default.
"""
DEFAULT_DATABASE = "biobank"
def create_schema(database):
	"""
	Create the schema in the given database.
	It is assumed that the database exists.
	This function can be used to create a test environment, refreshing the schema in just one database.

	:param database: The name of the database that will be used for the setup.
	:type database: str
	"""
	try:
		connection = PostgreSQLConnection.connect(database)

		"""
		Create the users' tables.
		"""

		"""
		Drop the user roles if they exist.
		"""
		connection.execute("""DROP TYPE IF EXISTS user_role CASCADE""")
		connection.execute("""CREATE TYPE user_role AS ENUM ('BIOBANKER', 'RESEARCHER', 'PARTICIPANT')""")

		"""
		Drop the user table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS users CASCADE;""")
		"""
		Create a new table with the most basic and required user fields.
		"""
		connection.execute("""CREATE TABLE users (
							user_id 			VARCHAR(64)		PRIMARY KEY,
							role				user_role
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN users.user_id IS 'The user''s unique identifier - a username or a pseudo-ID';""")
		connection.execute("""COMMENT ON COLUMN users.role IS 'The user''s role';""")

		"""
		Create the specific user role tables.
		This follows generalization specialization relational modeling (http://www.javaguicodexample.com/erdrelationalmodelnotes1.html).
		The biobanker does not require any additional fields.
		The participant does not require any additional fields.
		"""

		"""
		Drop the researcher table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS researchers CASCADE;""")
		"""
		Create the researchers table.
		When a user is deleted, their corresponding researcher-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE researchers (
							user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN researchers.user_id IS 'The researcher''s unique identifier, links to the ''users'' table''s primary key';""")

		"""
		Drop the participants table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS participants CASCADE;""")
		"""
		Create the participants table.
		When a user is deleted, their corresponding participant-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE participants (
							user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE,
							first_name			VARCHAR(256),
							last_name			VARCHAR(256),
							email				VARCHAR(256)
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN participants.user_id IS 'The participant''s unique identifier, links to the ''users'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN participants.first_name IS 'The participant''s first name';""")
		connection.execute("""COMMENT ON COLUMN participants.last_name IS 'The participant''s last name';""")
		connection.execute("""COMMENT ON COLUMN participants.email IS 'The participant''s email address';""")

		"""
		Drop the participants' identities table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS participant_identities CASCADE;""")
		"""
		Create the table that links participants with their blockchain identities.
		When a user is deleted, their corresponding participant-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE participant_identities (
							participant_id		VARCHAR(64)		REFERENCES participants(user_id)	ON DELETE CASCADE,
							address				VARCHAR(128)	UNIQUE,
							temp_card			BYTEA,
							cred_card			BYTEA
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN participant_identities.participant_id IS 'The participant''s unique identifier, links to the ''participants'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN participant_identities.address IS 'The participant''s address on the Hyperledger Fabric blockchain';""")
		connection.execute("""COMMENT ON COLUMN participant_identities.temp_card IS 'The participant''s Hyperledger card, created when their identity is issued; they need to import it into the wallet in order to get a credential-ready version';""")
		connection.execute("""COMMENT ON COLUMN participant_identities.cred_card IS 'The participant''s credential-ready Hyperledger card, created when the temporary card is imported, pinged and assigned credentials';""")


		"""
		Drop the participants' identities table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS participant_identities_eth CASCADE;""")
		"""
		Create the table that links participants with their blockchain identities.
		When a user is deleted, their corresponding participant-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE participant_identities_eth (
							participant_id		VARCHAR(64)		REFERENCES participants(user_id)	ON DELETE CASCADE,
							address				VARCHAR(32)		UNIQUE,
							private_key			VARCHAR(64)
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN participant_identities_eth.participant_id IS 'The participant''s unique identifier, links to the ''participants'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN participant_identities_eth.address IS 'The participant''s address on the Hyperledger Fabric blockchain';""")
		connection.execute("""COMMENT ON COLUMN participant_identities_eth.private_key IS 'The participant''s credential-ready Hyperledger card, created when the temporary card is imported, pinged and assigned credentials';""")

		"""
		Drop the participants' subscriptions table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS participant_subscriptions CASCADE;""")
		"""
		Create the table that links participants with their email subscriptions.
		When a user is deleted, their corresponding participant-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE participant_subscriptions (
							participant_id		VARCHAR(64)		REFERENCES participants(user_id)	ON DELETE CASCADE	PRIMARY KEY,
							any_email			BOOLEAN			DEFAULT TRUE
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN participant_subscriptions.participant_id IS 'The participant''s unique identifier, links to the ''participants'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN participant_subscriptions.any_email IS 'A boolean indicating whether the participant is subscribed to emails at all—
			if it is true, the granularity may be controlled using other columns;
			if it is false, the user receives no emails at all';""")

		"""
		Drop the biobankers table if it exists.
		"""
		connection.execute("""DROP TABLE IF EXISTS biobankers CASCADE;""")
		"""
		Create the biobankers table.
		When a user is deleted, their corresponding biobanker-specific data should also be removed.
		"""
		connection.execute("""CREATE TABLE biobankers (
							user_id				VARCHAR(64)		UNIQUE		REFERENCES users(user_id)		ON DELETE CASCADE
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN biobankers.user_id IS 'The biobanker''s unique identifier, links to the ''users'' table''s primary key';""")

		"""
		Create the studies' table.
		"""

		connection.execute("""DROP TABLE IF EXISTS studies CASCADE;""")
		connection.execute("""CREATE TABLE studies (
							study_id			VARCHAR(128)		PRIMARY KEY,
							name				VARCHAR(256),
							description			TEXT				NOT NULL,
							homepage			VARCHAR(512),
							attachment 			VARCHAR(1024),
							recruiting			BOOLEAN				DEFAULT TRUE
		);""")
		connection.execute("""COMMENT ON COLUMN studies.study_id IS 'The study''s unique identifier';""")
		connection.execute("""COMMENT ON COLUMN studies.name IS 'The study''s name';""")
		connection.execute("""COMMENT ON COLUMN studies.description IS 'A description of what the study is about';""")
		connection.execute("""COMMENT ON COLUMN studies.homepage IS 'A URL from where participants can obtain more information about the study';""")
		connection.execute("""COMMENT ON COLUMN studies.attachment IS 'A URL to an attachment related to the study, such as a PDF';""")
		connection.execute("""COMMENT ON COLUMN studies.recruiting IS 'A boolean indicating whether the study is recruiting research partners';""")

		"""
		Create the relation table joining researchers with studies.
		A researcher may only view studies in which they are participating.
		"""

		connection.execute("""DROP TABLE IF EXISTS studies_researchers;""")
		connection.execute("""CREATE TABLE studies_researchers (
							study_id			VARCHAR(128)	REFERENCES studies(study_id) ON DELETE CASCADE,
							researcher_id		VARCHAR(64)		REFERENCES researchers(user_id) ON DELETE CASCADE
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN studies_researchers.study_id IS 'The study''s unique identifier, links to the ''studies'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN studies_researchers.researcher_id IS 'The researcher''s unique identifier, links to the ''researchers'' table''s primary key';""")

		"""
		Emails.
		"""

		"""
		Create the email relation.
		An email is essentialy made up of a subject and a body.
		The recipients are stored in a separate relation.
		"""

		connection.execute("""DROP TABLE IF EXISTS emails CASCADE;""")
		connection.execute("""CREATE TABLE emails (
							id				SERIAL							PRIMARY KEY,
							subject			VARCHAR(1024)					NOT NULL,
							body			TEXT							NOT NULL,
							created_at		TIMESTAMP WITHOUT TIME ZONE		DEFAULT NOW()
		);""")

		"""
		Add comments to describe the columns.
		"""
		connection.execute("""COMMENT ON COLUMN emails.id IS 'The email''s unique ID and primary key';""")
		connection.execute("""COMMENT ON COLUMN emails.subject IS 'The subject of the email';""")
		connection.execute("""COMMENT ON COLUMN emails.body IS 'The body of the email';""")
		connection.execute("""COMMENT ON COLUMN emails.created_at IS 'The date and time when the email was created, which defaults to the date and time when the row was created.';""")

		"""
		Create the email recipient relation.
		This relation links emails with their recipients.
		It also stores a boolean flag that marks whether the email has been sent or not.
		The primary key is a compound key made up of the email ID and the recipient.
		This structure prevents double-sending emails to the same recipient.
		"""

		connection.execute("""DROP TABLE IF EXISTS email_recipients;""")
		connection.execute("""CREATE TABLE email_recipients (
							email_id		INTEGER			REFERENCEs emails(id) ON DELETE CASCADE,
							recipient		VARCHAR(1024)	NOT NULL,
							sent			BOOLEAN			DEFAULT FALSE,
							PRIMARY KEY(email_id, recipient)
		);""")

		connection.execute("""COMMENT ON COLUMN email_recipients.email_id IS 'The email''s unique identifier, links to the ''emails'' table''s primary key';""")
		connection.execute("""COMMENT ON COLUMN email_recipients.recipient IS 'The email address of a recipient who is meant to receive the email';""")
		connection.execute("""COMMENT ON COLUMN email_recipients.sent IS 'A boolean indicating whether the email has been sent to the recipient';""")

		"""
		When a user is removed from the users table, the deletion effect cascades.
		However, the inverse is not true.
		This trigger removes a user from the users table when the user is removed from a more specific table (participants, biobankers, researchers).
		"""
		connection.execute("""
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
	except Exception as e:
		print(e)

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:
		- -d --database	The database where to create the schema.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Create the database schema.")
	parser.add_argument("-d", "--database", help="<Required> The database where to create the schema.", required=True)
	args = parser.parse_args()
	return args

if __name__ == "__main__":
	args = setup_args()
	create_schema(args.database)
