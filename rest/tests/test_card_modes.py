"""
Test the different card modes of the biobank REST API.
"""

import json
import os
import sys
import time
import zipfile

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

	"""
	Actual tests.
	"""

	@abstractmethod
	def test_get_address(self):
		"""
		Test getting an address from the backend.
		"""

		pass

	@abstractmethod
	def test_different_studies_addresses(self):
		"""
		Test how getting addresses for different studies differs depending on the card mode.
		"""

		pass

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

	def test_get_address(self):
		"""
		Test getting an address from the backend.
		"""

		with rest_context(2323, 2323, CardModeTest._study_ids[0]) as address:
			self.assertTrue(len(address))

	def test_different_studies_addresses(self):
		"""
		Test that requesting the addresses for different studies returns the same address.
		"""

		with rest_context(2323, 2323, CardModeTest._study_ids[0]) as address_1:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "give_consent", {
				"study_id": CardModeTest._study_ids[0],
				"address": address_1,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			"""
			Wait for the consent to be effected.
			"""

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": CardModeTest._study_ids[0],
				"address": address_1,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			"""
			Fetch the card for a different study and ensure that the address is the same.
			"""
			token = self._get_access_token(["change_card"], "p2323")["access_token"]
			response = self.send_request("GET", "get_card", {
				"username": "p2323",
				"study_id": CardModeTest._study_ids[1],
				"temp": False,
			}, token)
			card = response.content

			"""
			Save it temporarily.
			"""
			script_dir = os.path.dirname(os.path.realpath(__file__))
			with open(os.path.join(script_dir, "cards", "temp.card"), "wb") as f:
				f.write(card)

			"""
			Read the card and unzip it.
			From the `metadata.json` file, extract  the participant's address.
			"""
			path = os.path.join(script_dir, 'cards', 'temp.card')
			with zipfile.ZipFile(path, 'r') as zip:
				with zip.open('metadata.json') as metadata:
					data = metadata.readline()
					address_2 = json.loads(data)['userName']

					"""
					Check that the addresses are the same.
					"""
					self.assertEqual(address_1, address_2)

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

	def test_get_address(self):
		"""
		Test getting an address from the backend.
		"""

		with rest_context(2323, 2323, CardModeTest._study_ids[0]) as address:
			self.assertTrue(len(address))

	def test_different_studies_addresses(self):
		"""
		Test that requesting the addresses for different studies returns different addresses.
		"""

		with rest_context(2323, 2323, CardModeTest._study_ids[0]) as address_1:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "give_consent", {
				"study_id": CardModeTest._study_ids[0],
				"address": address_1,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			"""
			Wait for the consent to be effected.
			"""

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": CardModeTest._study_ids[0],
				"address": address_1,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			"""
			Fetch the card for a different study and ensure that the address is the same.
			"""
			token = self._get_access_token(["change_card"], "p2323")["access_token"]
			response = self.send_request("GET", "get_card", {
				"username": "p2323",
				"study_id": CardModeTest._study_ids[1],
				"temp": False,
			}, token)
			card = response.content

			"""
			Save it temporarily.
			"""
			script_dir = os.path.dirname(os.path.realpath(__file__))
			with open(os.path.join(script_dir, "cards", "temp.card"), "wb") as f:
				f.write(card)

			"""
			Read the card and unzip it.
			From the `metadata.json` file, extract  the participant's address.
			"""
			path = os.path.join(script_dir, 'cards', 'temp.card')
			with zipfile.ZipFile(path, 'r') as zip:
				with zip.open('metadata.json') as metadata:
					data = metadata.readline()
					address_2 = json.loads(data)['userName']

					"""
					Check that the addresses are the same.
					"""
					self.assertNotEqual(address_1, address_2)
