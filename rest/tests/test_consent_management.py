"""
Test the dynamic consent management functionality in the backend.
"""

import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

from biobank.handlers.exceptions import study_exceptions, user_exceptions
from server.exceptions import request_exceptions

from .environment import *

from .test import BiobankTestCase, rest_context

class ConsentManagementTest(BiobankTestCase):
	"""
	Test the dynamic consent management functionality of the biobank backend.

	:cvar _study_ids: A list of study IDs that are used in the test cases.
	:vartype _study_ids: list of str
	"""

	_study_ids = []

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self):
		"""
		Connect with the database, create the schema and start the server.
		Then, generate some basic data.
		"""

		super(ConsentManagementTest, self).setUpClass()
		self.seed()

	@classmethod
	def tearDownClass(self):
		"""
		At the end of the tests, stop the server and kill all subprocesses.
		"""

		super(ConsentManagementTest, self).tearDownClass()

	@classmethod
	def seed(self):
		"""
		Seed the database before tests.
		"""

		self = ConsentManagementTest()
		token = self._get_access_token(
			["change_card", "create_study", "view_study", "create_participant"])["access_token"]

		ConsentManagementTest._study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name(),
		]

		"""
		Create the initial data.
		"""

		response = self.send_request("POST", "study", {
			"study_id": ConsentManagementTest._study_ids[0],
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "study", {
			"study_id": ConsentManagementTest._study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "study", {
			"study_id": ConsentManagementTest._study_ids[2],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "study", {
			"study_id": ConsentManagementTest._study_ids[3],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[2] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[3] }, token)

		"""
		Create two participants - `p2322` and `p2323`.
		"""

		for participant in [2322, 2323]:
			response = self.send_request("POST", "participant", {
				"username": f"p{participant}",
				"name": participant,
				"email": f"participant@test.com"
			}, token)
			self.assertEqual(response.status_code, 200)

	"""
	Actual tests.
	"""

	def test_give_consent_of_inexistent_participant(self):
		"""
		Test giving basic consent when the participant does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2321")["access_token"]
		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"address": "p2321",
			"access_token": None,
			"port": 3001,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantAddressDoesNotExistException.__name__)

	def test_give_consent_to_inexistent_study(self):
		"""
		Test giving basic consent when the study does not exist.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "give_consent", {
				"study_id": "!" + ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 500)
			self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

	def test_give_consent(self):
		"""
		Test giving basic consent.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

	def test_withdraw_consent_if_participant_does_not_exist(self):
		"""
		Test withdrawing basic consent when the participant does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2321")["access_token"]
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"address": "p2321",
			"access_token": None,
			"port": 3001,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantAddressDoesNotExistException.__name__)

	def test_withdraw_consent_to_inexistent_study(self):
		"""
		Test withdrawing basic consent when the study does not exist.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "withdraw_consent", {
				"study_id": "!" + ConsentManagementTest._study_ids[2],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 500)
			self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

	def test_withdraw_consent(self):
		"""
		Test withdrawing consent.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

	def test_give_and_withdraw_consent(self):
		"""
		Test withdrawing consent after giving it.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)

			if body["data"]:
				"""
				If the participant has already given consent, withdraw it first.
				"""

				response = self.send_request("POST", "withdraw_consent", {
					"study_id": ConsentManagementTest._study_ids[1],
					"address": address,
					"access_token": None,
					"port": 2323,
				}, token)
				body = response.json()
				self.assertEqual(response.status_code, 200)

				response = self.send_volatile_request("GET", "has_consent", {
					"study_id": ConsentManagementTest._study_ids[1],
					"address": address,
					"access_token": "None",
					"port": 2323,
				}, token, value=False)
				body = response.json()
				self.assertEqual(response.status_code, 200)
				self.assertFalse(body["data"])

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

	def test_check_consent_of_inexistent_participant(self):
		"""
		Consent cannot be checked if the participant does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2321")["access_token"]
		response = self.send_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"address": "p2321",
			"access_token": None,
			"port": 3001,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantAddressDoesNotExistException.__name__)

	def test_check_consent_of_inexistent_study(self):
		"""
		Consent cannot be checked if the study does not exist.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_request("GET", "has_consent", {
				"study_id": "!" + ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 500)
			self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

	def test_default_consent(self):
		"""
		By default, there should be no consent.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[2],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

	def test_get_participants_consented_studies(self):
		"""
		Test getting the studies that the participant consented to.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:

			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			"""
			Give consent to one study.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

			"""
			Get the user's studies.
			"""

			response = self.send_request("GET", "get_studies_by_participant", {
				"username": "p2323",
				"access_token": token,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)
			body = response.json()["data"]
			self.assertEqual(len(body), 1)

			"""
			Give consent to another study.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			response = self.send_request("GET", "get_studies_by_participant", {
				"username": "p2323",
				"access_token": token,
				"port": 2323,
			}, token)
			body = response.json()["data"]
			self.assertEqual(response.status_code, 200)
			self.assertEqual(len(body), 2)

	def test_get_participants_from_inexistent_study(self):
		"""
		Test getting the participants from an inexistent study.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "admin")["access_token"]
		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": "!" + ConsentManagementTest._study_ids[0],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

	def test_give_consent_on_behalf(self):
		"""
		Test that giving consent on behalf of someone fails.
		"""

		with rest_context(2322, 2322, ConsentManagementTest._study_ids[1]) as p2322_address,\
			 rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as p2323_address:

			p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
			p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			"""
			Give consent for `p2323`.
			"""
			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2322_token)
			body = response.json()
			self.assertEqual(response.status_code, 401)
			self.assertEqual(body["exception"], request_exceptions.UnauthorizedDataAccessException.__name__)

	def test_withdraw_consent_on_behalf(self):
		"""
		Test that withdrawing consent on behalf of someone fails.
		"""

		with rest_context(2322, 2322, ConsentManagementTest._study_ids[1]) as p2322_address,\
			 rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as p2323_address:

			p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
			p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			"""
			Withdraw consent for `p2323`.
			"""
			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2322_token)
			body = response.json()
			self.assertEqual(response.status_code, 401)
			self.assertEqual(body["exception"], request_exceptions.UnauthorizedDataAccessException.__name__)

	def test_check_consent_on_behalf(self):
		"""
		Test that checking consent on behalf of someone fails.
		"""

		with rest_context(2322, 2322, ConsentManagementTest._study_ids[1]) as p2322_address,\
			 rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as p2323_address:

			p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
			p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			"""
			Check consent of `p2323`.
			"""
			response = self.send_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[0],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2322_token)
			body = response.json()
			self.assertEqual(response.status_code, 401)
			self.assertEqual(body["exception"], request_exceptions.UnauthorizedDataAccessException.__name__)

	def test_get_participants_consented_studies_on_behalf(self):
		"""
		Test that getting the studies that another participant consented to fails.
		"""

		with rest_context(2322, 2322, ConsentManagementTest._study_ids[1]) as p2322_address,\
			 rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as p2323_address:

			p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
			p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			response = self.send_request("GET", "get_studies_by_participant", {
				"username": "p2322",
				"access_token": "None",
				"port": 2322,
			}, p2323_token)
			body = response.json()
			self.assertEqual(response.status_code, 401)
			self.assertEqual(body["exception"], request_exceptions.UnauthorizedDataAccessException.__name__)

	def test_get_study_participants(self):
		"""
		Test getting the participants that have consented to the use of their samples in a study.
		"""

		with rest_context(2322, 2322, ConsentManagementTest._study_ids[1]) as p2322_address,\
			 rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as p2323_address:

			p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
			p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			token = self._get_access_token(["update_consent", "view_consent"], "admin")["access_token"]

			"""
			Assert that there are no participants in the study yet.
			"""

			response = self.send_request("GET", "get_participants_by_study", {
				"study_id": ConsentManagementTest._study_ids[3],
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertEqual(len(body['data']), 0)

			"""
			Give consent from `p2322`.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2322_address,
				"access_token": None,
				"port": 2322,
			}, p2322_token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2322_address,
				"access_token": "None",
				"port": 2322,
			}, p2322_token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			"""
			Give consent from `p2323`.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2323_token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": "None",
				"port": 2323,
			}, p2323_token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			"""
			Check that the two appear in the study.
			"""

			response = self.send_request("GET", "get_participants_by_study", {
				"study_id": ConsentManagementTest._study_ids[3],
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(any(user["user_id"] == "p2322" for user in body["data"]))
			self.assertTrue(any(user["user_id"] == "p2323" for user in body["data"]))

			"""
			Withdraw consent from `p2322`.
			"""

			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2322_address,
				"access_token": None,
				"port": 2322,
			}, p2322_token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2322_address,
				"access_token": "None",
				"port": 2322,
			}, p2322_token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

			"""
			Withdraw consent from `p2323`.
			"""

			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2323_token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": "None",
				"port": 2323,
			}, p2323_token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

			"""
			Check that the study now appears to have no participants.
			"""

			response = self.send_request("GET", "get_participants_by_study", {
				"study_id": ConsentManagementTest._study_ids[3],
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertEqual(len(body['data']), 0)

			"""
			Give consent from `p2323`.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": None,
				"port": 2323,
			}, p2323_token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[3],
				"address": p2323_address,
				"access_token": "None",
				"port": 2323,
			}, p2323_token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			"""
			Check that participant p2323 appears in the list of participants now.
			"""

			response = self.send_request("GET", "get_participants_by_study", {
				"study_id": ConsentManagementTest._study_ids[3],
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(any(user["user_id"] == "p2323" for user in body["data"]))

	"""
	Consent Trail.
	"""

	def test_get_consent_trail(self):
		"""
		Test getting the consent trail of a user.
		"""

		with rest_context(2323, 2323, ConsentManagementTest._study_ids[1]) as address:
			token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

			"""
			In the beginning, the consent trail should be empty.
			"""

			response = self.send_request("GET", "get_consent_trail", {
				"username": "p2323",
				"access_token": "None",
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual({}, body['data']['timeline'])

			"""
			After giving consent, the timeline should have this new consent change.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			response = self.send_request("GET", "get_consent_trail", {
				"username": "p2323",
				"access_token": "None",
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(1, len(body['data']['timeline']))
			for i, timestamp in enumerate(sorted(body['data']['timeline'].keys())):
				self.assertEqual(not (i % 2), body['data']['timeline'][timestamp][ConsentManagementTest._study_ids[1]])

			"""
			Withdraw consent, and the timeline should have this new consent change.
			"""

			response = self.send_request("POST", "withdraw_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

			response = self.send_request("GET", "get_consent_trail", {
				"username": "p2323",
				"access_token": "None",
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(2, len(body['data']['timeline']))
			for i, timestamp in enumerate(sorted(body['data']['timeline'].keys())):
				self.assertEqual(not (i % 2), body['data']['timeline'][timestamp][ConsentManagementTest._study_ids[1]])

			"""
			Give consent once more, and the timeline should have this new consent change.
			"""

			response = self.send_request("POST", "give_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": None,
				"port": 2323,
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"address": address,
				"access_token": "None",
				"port": 2323,
			}, token, value=True)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertTrue(body["data"])

			response = self.send_request("GET", "get_consent_trail", {
				"username": "p2323",
				"access_token": "None",
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(3, len(body['data']['timeline']))
			for i, timestamp in enumerate(sorted(body['data']['timeline'].keys())):
				self.assertEqual(not (i % 2), body['data']['timeline'][timestamp][ConsentManagementTest._study_ids[1]])
