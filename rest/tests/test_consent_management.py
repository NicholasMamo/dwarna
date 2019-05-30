"""
Test the dynamic consent management functionality in the backend.
"""

from datetime import datetime, timedelta
import json
import os
import signal
import subprocess
import sys
import time

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

from psycopg2 import InternalError

import main

from biobank.handlers.exceptions import general_exceptions, study_exceptions, user_exceptions
from server.exceptions import request_exceptions

from .environment import *

from .test import BiobankTestCase

class ConsentManagementTest(BiobankTestCase):
	"""
	Test the dynamic consent management functionality of the biobank backend.

	:cvar _subprocesses: A list of running subprocesses.
	:vartype _subprocesses: list
	"""

	_subprocesses = []

	_study_ids = []

	@classmethod
	@BiobankTestCase.isolated_test
	def setUpClass(self):
		"""
		Connect with the database, create the schema and start the server.
		Then, generate some basic data.
		"""

		super(ConsentManagementTest, self).setUpClass()

		self = ConsentManagementTest()
		token = self._get_access_token(
			["change_card", "create_study", "view_study", "create_participant"])["access_token"]

		ConsentManagementTest._study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name()
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

		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": ConsentManagementTest._study_ids[2] }, token)

		"""
		Create two participants, fetch their cards and start REST servers for them.

			- Participant `p2322` served on port 2322; and
			- Participant `p2323` served on port 2323
		"""

		for participant in [2322, 2323]:
			response = self.send_request("POST", "participant", {
				"username": f"p{participant}"
			}, token)
			self.assertEqual(response.status_code, 200)

			response = self.send_request("GET", "get_card", {
				"username": f"p{participant}",
				"temp": True
			}, token)
			self.assertEqual(response.status_code, 200)
			self.save_card(response.content, f"p{participant}.card")
			self.start_rest(f"p{participant}.card", participant)

	@classmethod
	def tearDownClass(self):
		"""
		At the end of the tests, stop the server and kill all subprocesses.
		"""

		super(ConsentManagementTest, self).tearDownClass()

		for proc in ConsentManagementTest._subprocesses:
			pid = proc.pid
			proc.kill()
			out, _ = proc.communicate()
			proc.wait()

		ports = [2322, 2323]
		for port in ports:
			cmd = f"kill $( lsof -i:{port} -t )"
			proc = subprocess.check_output(["bash", "-i", "-c", cmd])

	def save_card(self, card, card_name, dir="cards"):
		"""
		Save the provided card to a file.

		:param card: The card data to save.
		:type card: bytes
		:param card_name: The target filename.
		:type card_name: str
		:param dir: The target directory, relative to this script.
		:type dir: str
		"""

		script_dir = os.path.dirname(os.path.realpath(__file__))
		with open(os.path.join(script_dir, dir, card_name), "wb") as f:
			f.write(card)

	def start_rest(self, card_name, port):
		"""
		Start the REST API using the given card name.

		:param card_name: The target filename.
		:type card_name: str
		:param port: The port where to open the REST API.
		:type port: int
		"""

		script_dir = os.path.dirname(os.path.realpath(__file__))
		proc = subprocess.Popen([
				"bash", os.path.join(script_dir, "start_rest.sh"),
				card_name, str(port)
			], close_fds=True)
			# stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		ConsentManagementTest._subprocesses.append(proc)
		pid = proc.pid
		time.sleep(10)

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
			"username": "p2321",
			"access_token": None,
			"port": 2323,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

	def test_give_consent_to_inexistent_study(self):
		"""
		Test giving basic consent when the study does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("POST", "give_consent", {
			"study_id": "!" + ConsentManagementTest._study_ids[1],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
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
			"username": "p2321",
			"access_token": None,
			"port": 2323,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

	def test_withdraw_consent_if_study_does_not_exist(self):
		"""
		Test withdrawing basic consent when the study does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "!" + ConsentManagementTest._study_ids[2],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
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
				"username": "p2323",
				"access_token": None,
				"port": 2323,
			}, token)
			body = response.json()
			self.assertEqual(response.status_code, 200)

			response = self.send_volatile_request("GET", "has_consent", {
				"study_id": ConsentManagementTest._study_ids[1],
				"username": "p2323",
				"access_token": "None",
				"port": 2323,
			}, token, value=False)
			body = response.json()
			self.assertEqual(response.status_code, 200)
			self.assertFalse(body["data"])

		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": "None",
			"port": 2323,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
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
			"username": "p2321",
			"access_token": None,
			"port": 2323,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

	def test_check_consent_of_inexistent_study(self):
		"""
		Consent cannot be checked if the study does not exist.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_request("GET", "has_consent", {
			"study_id": "!" + ConsentManagementTest._study_ids[1],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]
		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[2],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

		"""
		Give consent to one study.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[1],
			"username": "p2323",
			"access_token": "None",
			"port": 2323,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
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
			"access_token": "None",
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
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": "None",
			"port": 2323,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_studies_by_participant", {
			"username": "p2323",
			"access_token": "None",
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

		p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]

		"""
		Give consent for `p2323`.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
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

		p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]

		"""
		Withdraw consent for `p2323`.
		"""
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
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

		p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]

		"""
		Check consent of `p2323`.
		"""
		response = self.send_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
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

		token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

		response = self.send_request("GET", "get_studies_by_participant", {
			"username": "p2322",
			"access_token": "None",
			"port": 2322,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 401)
		self.assertEqual(body["exception"], request_exceptions.UnauthorizedDataAccessException.__name__)

	def no_test_get_study_participants(self):
		"""
		Test getting the participants that have consented to the use of their samples in a study.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "admin")["access_token"]
		p2322_token = self._get_access_token(["update_consent", "view_consent"], "p2322")["access_token"]
		p2323_token = self._get_access_token(["update_consent", "view_consent"], "p2323")["access_token"]

		"""
		Give consent from `p2322`.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2322",
			"access_token": None,
			"port": 2322,
		}, p2322_token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2322",
			"access_token": "None",
			"port": 2322,
		}, p2322_token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		"""
		Withdraw consent from `p2323`.
		"""

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, p2323_token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": "None",
			"port": 2323,
		}, p2323_token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": ConsentManagementTest._study_ids[0],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(any(user["user_id"] == "p2322" for user in body["data"]))
		self.assertFalse(any(user["user_id"] == "p2323" for user in body["data"]))

		"""
		Withdraw consent from `p2322`.
		"""

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2322",
			"access_token": None,
			"port": 2322,
		}, p2322_token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2322",
			"access_token": "None",
			"port": 2322,
		}, p2322_token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		Give consent from `p2323`.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": None,
			"port": 2323,
		}, p2323_token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": ConsentManagementTest._study_ids[0],
			"username": "p2323",
			"access_token": "None",
			"port": 2323,
		}, p2323_token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": ConsentManagementTest._study_ids[0],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(any(user["user_id"] == "p2323" for user in body["data"]))
		self.assertFalse(any(user["user_id"] == "p2322" for user in body["data"]))
