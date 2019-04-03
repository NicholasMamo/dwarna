import os
from os.path import expanduser

import psycopg2

from setup import minimal_schema, oauth_schema

"""
The databases that are used as a testing environment.
"""
TEST_DATABASE = "biobank_test"
TEST_OAUTH_DATABASE = "biobank_oauth_test"

"""
The port where the tests will be held.
"""
PORT = 2321

"""
The client's ID.
"""
CLIENT_ID = "abc"

"""
The client's secret.
"""
CLIENT_SECRET = "xyz"

cursor, con = None, None

def create_testing_environment():
	"""
	Create a testing environment so that the actual database is not altered.
	"""

	global cursor, con

	# get the connection details from the .pgpass file
	home = expanduser("~")
	with open(os.path.join(home, ".pgpass"), "r") as f:
		host, port, database, username, password = f.readline().strip().split(":")
		con = psycopg2.connect(dbname=database, user=username, host=host, password=password)

		con.autocommit = True # commit all changes automatically
		cursor = con.cursor() # fetch the cursor

		"""
		Ensure that the database does not already exist.
		Create it only if it doesn't exist.
		"""
		cursor.execute("""SELECT 1 FROM pg_database WHERE datname = '%s'""" % TEST_DATABASE)
		print("Database has to be created" if not cursor.rowcount else "Database already exists")
		if (cursor.rowcount == 0):
			cursor.execute("CREATE DATABASE %s" % TEST_DATABASE)
		minimal_schema.create_schema(TEST_DATABASE)

		cursor.execute("""SELECT 1 FROM pg_database WHERE datname = '%s'""" % TEST_OAUTH_DATABASE)
		print("Database has to be created" if not cursor.rowcount else "Database already exists")
		if (cursor.rowcount == 0):
			cursor.execute("CREATE DATABASE %s" % TEST_OAUTH_DATABASE)
		oauth_schema.create_schema(TEST_OAUTH_DATABASE)

		con = psycopg2.connect(dbname=TEST_DATABASE, user=username, host=host, password=password)
		cursor = con.cursor() # fetch the cursor

def clear():
	"""
	Clear all the data from the database.
	"""

	cursor.execute("DELETE FROM users")
	cursor.execute("DELETE FROM studies")
	cursor.execute("ALTER SEQUENCE studies_study_id_seq RESTART WITH 1")
	con.commit()
