"""
Test the different card modes of the biobank REST API.
"""

import os
import sys
import time

from abc import ABC, abstractmethod

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

	:cvar _study_ids: A list of study IDs that are used in the test cases.
	:vartype _study_ids: list of str
	"""

	_study_ids = []

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self, single_card=True):
		"""
		Connect with the database, create the schema and start the server.

		:param single_card: A boolean indicating whether the REST API should be started in single-card mode.
							If false, the REST API is started in multi-card mode.
		:type single_card: bool
		"""

		create_testing_environment()
		main.main(TEST_DATABASE, TEST_OAUTH_DATABASE, PORT, single_card=single_card)
		time.sleep(1) # wait so as not to overload the server with requests
		CardModeTest.seed()

	@classmethod
	def seed(self):
		"""
		Seed the database before tests.
		"""
		self = BiobankTestCase()
		token = self._get_access_token(
		["change_card", "create_study", "view_study", "create_participant"])["access_token"]

		CardModeTest._study_ids = [
		self._generate_study_name(),
		self._generate_study_name(),
		self._generate_study_name(),
		self._generate_study_name(),
		]

		"""
		Create the initial data.
		"""

		response = self.send_request("POST", "study", {
		"study_id": CardModeTest._study_ids[0],
		"name": "ALS",
		"description": "ALS Study",
		"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "study", {
		"study_id": CardModeTest._study_ids[1],
		"name": "Diabetes",
		"description": "Diabetes study",
		"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the data was created.
		"""

		response = self.send_volatile_request("GET", "study", { "study_id": CardModeTest._study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": CardModeTest._study_ids[1] }, token)

		"""
		Create a participant - `p2323`.
		"""

		for participant in [2323]:
			response = self.send_request("POST", "participant", {
			"username": f"p{participant}",
			"name": participant,
			"email": f"participant@test.com"
			}, token)
			self.assertEqual(response.status_code, 200)


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
