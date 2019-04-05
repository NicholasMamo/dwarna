"""
Create the database that stores access tokens.
Implementation based on https://github.com/wndhydrnt/python-oauth2/blob/v1/oauth2/store/dbapi/mysql.py.
"""

import os
from os.path import expanduser

import psycopg2

"""
The database used by default
"""
DEFAULT_DATABASE = "biobank_oauth"

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
			host, port, _, username, password = f.readline().strip().split(":")
			# establish a connection
			con = psycopg2.connect(dbname=database, user=username, host=host, password=password)
			# create a psycopg2 cursor that can execute queries
			cursor = con.cursor()

			"""
			Create the access tokens table.
			"""

			cursor.execute("""DROP TYPE IF EXISTS grant_type CASCADE""")
			cursor.execute("""CREATE TYPE grant_type AS ENUM ('authorization_code', 'implicit', 'password', 'client_credentials', 'refresh_token')""")

			cursor.execute("""DROP TABLE IF EXISTS access_tokens CASCADE;""")
			cursor.execute("""
				CREATE TABLE access_tokens (
					id 					SERIAL 			NOT NULL	PRIMARY KEY,
					client_id 			VARCHAR(32) 	NOT NULL,
					grant_type 			grant_type 		NOT NULL,
					token 				CHAR(36) 		NOT NULL,
					expires_at 			TIMESTAMP 		NULL,
					refresh_token 		CHAR(36) 		NULL,
					refresh_expires_at 	TIMESTAMP 		NULL,
					user_id 			VARCHAR(1024) 	NULL);
			""")

			# add the indices
			cursor.execute("""CREATE INDEX fetch_by_token ON access_tokens (token ASC);""")
			cursor.execute("""CREATE INDEX fetch_by_refresh_token ON access_tokens (refresh_token ASC);""")
			cursor.execute("""CREATE INDEX fetch_existing_token_of_user ON access_tokens (client_id ASC, grant_type ASC, user_id ASC);""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN access_tokens.id IS 'Unique identifier';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.client_id IS 'The identifier of a client. Assuming it is an arbitrary text which is a maximum of 32 characters long.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.grant_type IS 'The type of a grant for which a token has been issued.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.token IS 'The access token.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.expires_at IS 'The timestamp at which the token expires.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.refresh_token IS 'The refresh token.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.refresh_expires_at IS 'The timestamp at which the refresh token expires.';""")
			cursor.execute("""COMMENT ON COLUMN access_tokens.user_id IS 'The identifier of the user this token belongs to.';""")

			"""
			Create the scopes table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS access_token_scopes CASCADE;""")
			cursor.execute("""
				CREATE TABLE access_token_scopes (
					id 					SERIAL 			NOT NULL	PRIMARY KEY,
					name 				VARCHAR(32) 	NOT NULL,
					access_token_id 	INT 			NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN access_token_scopes.name IS 'The name of scope.';""")
			cursor.execute("""COMMENT ON COLUMN access_token_scopes.access_token_id IS 'The unique identifier of the access token this scope belongs to';""")

			"""
			Create the data table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS access_token_data CASCADE;""")
			cursor.execute("""
				CREATE TABLE access_token_data (
					id 					SERIAL		NOT NULL PRIMARY KEY,
					key 				VARCHAR(32)	NOT NULL,
					value 				VARCHAR(32)	NOT NULL,
					access_token_id 	INT 		NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN access_token_data.key IS 'The key of an entry converted to the key in a Python dict.';""")
			cursor.execute("""COMMENT ON COLUMN access_token_data.value IS 'The value of an entry converted to the value in a Python dict.';""")
			cursor.execute("""COMMENT ON COLUMN access_token_data.access_token_id IS 'The unique identifier of the access token a row belongs to.';""")

			"""
			Create the authorization code table, used in the three-legged OAuth 2.0 flow.
			"""
			cursor.execute("""DROP TABLE IF EXISTS auth_codes CASCADE;""")
			cursor.execute("""
				CREATE TABLE auth_codes (
					id 					SERIAL 			NOT NULL PRIMARY KEY,
					client_id			VARCHAR(32)		NOT NULL,
					code				CHAR(36)		NOT NULL,
					expires_at 			TIMESTAMP		NOT NULL,
					redirect_uri		VARCHAR(128)	NULL,
					user_id				INT				NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN auth_codes.client_id IS 'The identifier of a client. Assuming it is an arbitrary text which is a maximum of 32 characters long.';""")
			cursor.execute("""COMMENT ON COLUMN auth_codes.code IS 'The authorisation code.';""")
			cursor.execute("""COMMENT ON COLUMN auth_codes.expires_at IS 'The timestamp at which the token expires.';""")
			cursor.execute("""COMMENT ON COLUMN auth_codes.redirect_uri IS 'The redirect URI send by the client during the request of an authorisation code.';""")
			cursor.execute("""COMMENT ON COLUMN auth_codes.user_id IS 'The identifier of the user this authorisation code belongs to.';""")

			# add the index
			cursor.execute("""CREATE INDEX fetch_code ON auth_codes (code ASC);""")

			"""
			Create the authorization codes' data table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS auth_code_data CASCADE;""")
			cursor.execute("""
				CREATE TABLE auth_code_data (
					id					SERIAL 			NOT NULL PRIMARY KEY,
					key 				VARCHAR(32) 	NOT NULL,
					value 				VARCHAR(32) 	NOT NULL,
					auth_code_id 		INT 			NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN auth_code_data.key IS 'The key of an entry converted to the key in a Python dict.';""")
			cursor.execute("""COMMENT ON COLUMN auth_code_data.value IS 'The value of an entry converted to the value in a Python dict.';""")
			cursor.execute("""COMMENT ON COLUMN auth_code_data.auth_code_id IS 'The identifier of the authorisation code that this row belongs to.';""")

			"""
			Create the authorization codes' scopes table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS auth_code_scopes CASCADE;""")
			cursor.execute("""
				CREATE TABLE auth_code_scopes (
					id 					SERIAL			NOT NULL PRIMARY KEY,
					name 				VARCHAR(32) 	NOT NULL,
					auth_code_id 		INT 			NOT NULL);
			""")

			"""
			Create the clients database.
			"""
			cursor.execute("""DROP TABLE IF EXISTS clients CASCADE;""")
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS clients (
					id					SERIAL 			NOT NULL PRIMARY KEY,
					identifier 			VARCHAR(32) 	NOT NULL,
					secret 				VARCHAR(32) 	NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN clients.identifier IS 'The identifier of a client.';""")
			cursor.execute("""COMMENT ON COLUMN clients.secret IS 'The secret of a client.';""")

			"""
			Create the client grants table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS client_grants CASCADE;""")
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS client_grants (
					id					SERIAL 			NOT NULL PRIMARY KEY,
					name				VARCHAR(32)		NOT NULL,
					client_id			INT				NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN access_tokens.client_id IS 'The id of the client a row belongs to.';""")

			"""
			Create the clients' redirect URIs table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS client_redirect_uris CASCADE;""")
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS client_redirect_uris (
					id					SERIAL			NOT NULL PRIMARY KEY,
					redirect_uri 		VARCHAR(128)	NOT NULL,
					client_id 			INT				NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN client_redirect_uris.redirect_uri IS 'A URI of a client.';""")
			cursor.execute("""COMMENT ON COLUMN client_redirect_uris.client_id IS 'The id of the client a row belongs to.';""")

			"""
			Create the client response types table.
			"""
			cursor.execute("""DROP TABLE IF EXISTS client_response_types CASCADE;""")
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS client_response_types (
					id					SERIAL			NOT NULL PRIMARY KEY,
					response_type 		VARCHAR(32)		NOT NULL,
					client_id 			INT				NOT NULL);
			""")

			# explain the columns
			cursor.execute("""COMMENT ON COLUMN client_response_types.response_type IS 'The response type that a client can use.';""")
			cursor.execute("""COMMENT ON COLUMN client_response_types.client_id IS 'The id of the client a row belongs to.';""")

			con.commit() # commit the changes
	except Exception as e:
		print(e)

if __name__ == "__main__":
	create_schema(DEFAULT_DATABASE)
