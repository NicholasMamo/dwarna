"""
Test the different card modes of the biobank REST API.
"""

import os
import sys
import time

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from .environment import *

from .test import BiobankTestCase, rest_context

class CardModeTest(BiobankTestCase):
	"""
	An abstract class that describes the tests that should be created by card mode tests.
	"""

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self, single_card):
		"""
		Connect with the database, create the schema and start the server.

		:param single_card: A boolean indicating whether the REST API should be started in single-card mode.
							If false, the REST API is started in multi-card mode.
		:type single_card: bool
		"""

		create_testing_environment()
		main.main(TEST_DATABASE, TEST_OAUTH_DATABASE, PORT, single_card=single_card)
		time.sleep(1) # wait so as not to overload the server with requests

class SingleCardModeTest(CardModeTest):
	"""
	Tests for the single-card mode.
	"""

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self):
		"""
		Create the REST API in single-card mode.
		"""

		super(SingleCardModeTest, self).setUpClass(True)

class MultiCardModeTest(CardModeTest):
	"""
	Tests for the multi-card mode.
	"""

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self):
		"""
		Create the REST API in multi-card mode.
		"""

		super(MultiCardModeTest, self).setUpClass(False)
