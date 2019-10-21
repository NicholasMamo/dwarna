import os
import sys

from os.path import expanduser

import psycopg2

path = sys.path[0]
setup_path = os.path.join(path, "..")
if setup_path not in sys.path:
	sys.path.insert(1, setup_path)

rest_path = os.path.join(path, '..', '..', 'rest')
if rest_path not in sys.path:
	sys.path.insert(1, rest_path)

from connection.db_connection import PostgreSQLConnection
import minimal_schema

TEST_DATABASE = "biobank_test"
"""
The database that is used as a testing environment.
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

def clear():
	"""
	Clear all the data from the database.
	"""

	connection = PostgreSQLConnection.connect(TEST_DATABASE)

	connection.execute("DELETE FROM users")
	connection.execute("DELETE FROM studies")
	connection.execute("DELETE FROM emails")

if __name__ == "__main__":
	create_testing_environment()
