"""
Test the email schema.
The tests in this class concern not only the `emails` table, but also the `email_recipients` relation.
"""

import os
import sys

from functools import wraps

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import os
import psycopg2
import minimal_schema
import unittest

from .environment import *
from .test import SchemaTestCase

class EmailTests(SchemaTestCase):
	"""
	Test the email schema.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Set up the class to create the schema.
		"""

		super(StudyTests, self).setUpClass()

	def isolated_test(test):
		"""
		Perform the test in isolation.
		In essence, this means that the data is cleared from the database.
		Then, sample data is re-introduced.

		:param test: The test to perform.
		:type test: function
		"""

		@wraps(test)

		def wrapper(*args):
			"""
			The wrapper removes all data from the database.
			"""

			clear()
			self = args[0]
			test(*args)

		return wrapper

