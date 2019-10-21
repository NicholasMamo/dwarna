import os
from os.path import expanduser

import psycopg2
import sys

path = sys.path[0]
rest_path = os.path.join(path, "..")
if rest_path not in sys.path:
	sys.path.insert(1, rest_path)
setup_path = os.path.join(path, "..", "..")
if setup_path not in sys.path:
	sys.path.insert(1, setup_path)

from connection.db_connection import PostgreSQLConnection
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

def create_testing_environment():
	"""
	Create a testing environment so that the actual database is not altered.
	"""

	connection = PostgreSQLConnection.connect('postgres')

	"""
	Ensure that the database does not already exist.
	Create it only if it doesn't exist.
	"""
	exists = connection.exists("""SELECT 1 FROM pg_database WHERE datname = '%s'""" % TEST_DATABASE)
	print("Database has to be created" if not exists else "Database already exists")
	if (not exists):
		connection.execute("CREATE DATABASE %s" % TEST_DATABASE)
	minimal_schema.create_schema(TEST_DATABASE)

	exists = connection.exists("""SELECT 1 FROM pg_database WHERE datname = '%s'""" % TEST_OAUTH_DATABASE)
	print("Database has to be created" if not exists else "Database already exists")
	if (not exists):
		connection.execute("CREATE DATABASE %s" % TEST_OAUTH_DATABASE)
	oauth_schema.create_schema(TEST_OAUTH_DATABASE)

def clear():
	"""
	Clear all the data from the database.
	"""

	connection = PostgreSQLConnection.connect(TEST_DATABASE)

	connection.execute("DELETE FROM participant_identities")
	connection.execute("DELETE FROM users")
	connection.execute("DELETE FROM studies")
	connection.execute("DELETE FROM emails")
