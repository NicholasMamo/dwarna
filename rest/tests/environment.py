import os
from os.path import expanduser
import sys

path = sys.path[0]
path = os.path.join(path, "..", "..")
if path not in sys.path:
	sys.path.insert(1, path)

import psycopg2

from setup import minimal_schema, oauth_schema

TEST_DATABASE = "biobank_test"
"""
The database that is used as a testing environment.
"""

TEST_OAUTH_DATABASE = "biobank_oauth_test"
"""
The OAuth 2.0 database that is used for the testing environment.
"""

PORT = 3198
"""
The port where the tests will be held.
"""

CLIENT_ID = "abc"
"""
The client's ID.
"""

CLIENT_SECRET = "xyz"
"""
The client's secret.
"""

cursor, con = None, None

def create_testing_environment():
	"""
	Create a testing environment so that the actual database is not altered.
	"""

	con = get_connection("postgres")
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

	cursor.close()
	con.close()

def get_connection(database=TEST_DATABASE):
	# get the connection details from the .pgpass file
	home = expanduser("~")
	with open(os.path.join(home, ".pgpass"), "r") as f:
		host, port, _, username, password = f.readline().strip().split(":")
		con = psycopg2.connect(dbname=database, user=username, host=host, password=password)
	return con

def clear():
	"""
	Clear all the data from the database.
	"""

	con = get_connection()
	cursor = con.cursor() # fetch the cursor

	cursor.execute("DELETE FROM participant_identities")
	cursor.execute("DELETE FROM users")
	cursor.execute("DELETE FROM studies")
	con.commit()

	cursor.close()
	con.close()
