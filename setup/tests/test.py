"""
Creates the setup for the tests.
"""

import functools
import json
import os
import requests
import signal
import sys
import time
import unittest
import uuid

from functools import wraps

from .environment import *

path = sys.path[0]
rest_path = os.path.join(path, "..", "..", "rest")
if rest_path not in sys.path:
	sys.path.insert(1, rest_path)

from connection.db_connection import PostgreSQLConnection

class SchemaTestCase(unittest.TestCase):
	"""
	Test the schema.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Connect with the database and create the schema.
		"""

		create_testing_environment()

	def __del__(self):
		"""
		At the end of the tests, close the PostgreSQL connection and cursor.
		"""

		self._connection.close()

	def __init__(self, *args, **kwargs):
		"""
		Connect with the database and save the cursor.
		"""

		super(SchemaTestCase, self).__init__(*args, **kwargs)
		self._connection = PostgreSQLConnection.connect(TEST_DATABASE)

	def isolated_test(test):
		"""
		Perform the test in isolation.
		In essence, this means that the data is cleared from the database.

		:param test: The test to perform.
		:type test: function
		"""

		@wraps(test)

		def wrapper(*args):
			"""
			The wrapper removes all data from the database.
			"""

			clear()
			test(*args)

		return wrapper

	"""
	Make the isolated test a static method.
	NOTE: This should be done after the methods in this class that use this decorator have already been defined.
	"""
	isolated_test = staticmethod(isolated_test)

	def reconnect(self):
		"""
		Reconnect to the test database.
		"""

		self._connection.reconnect()

	def assert_fail_sql(self, sql, exception_name):
		"""
		Assert that the given SQL code fails with the given exception.
		At the end, reconnect with the database.

		:param sql: The SQL query to execute.
		:type sql: str
		:param exception_name: The expected exception name.
		:type exception_name: str
		"""

		try:
			self._connection.execute(sql)
		except Exception as e:
			try:
				self.assertEqual(type(e).__name__, exception_name)
			except AssertionError as a:
				self.fail(f"""Did not raise exception {exception_name}\nRaised instead {type(e).__name__}:\n\t{e}
				""")
		finally:
			self.reconnect()
