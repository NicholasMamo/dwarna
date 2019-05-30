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

from .environment import *

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

		self._cursor.close()
		self._con.close()

	def __init__(self, *args, **kwargs):
		"""
		Connect with the database and save the cursor.
		"""

		super(SchemaTestCase, self).__init__(*args, **kwargs)
		self.reconnect()

	def reconnect(self):
		"""
		Reconnect to the test database.
		"""

		try:
			# get the connection details from the .pgpass file
			home = expanduser("~")
			with open(os.path.join(home, ".pgpass"), "r") as f:
				host, port, _, username, password = f.readline().strip().split(":")
				self._con = psycopg2.connect(dbname=TEST_DATABASE, user=username, host=host, password=password)
				self._cursor = self._con.cursor()
		except Exception as e:
			print(e)

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
			self._cursor.execute(sql)
		except Exception as e:
			try:
				self.assertEqual(type(e).__name__, exception_name)
			except AssertionError as a:
				self.fail(f"""Did not raise exception {exception_name}\nRaised instead {type(e).__name__}:\n\t{e}
				""")
		finally:
			self.reconnect()
