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

	@classmethod
	def setUpClass(self):
		"""
		Connect with the database, create the schema and start the server.
		Then, generate some basic data.
		"""

		super(ConsentManagementTest, self).setUpClass()

		clear()

		self = ConsentManagementTest()
		token = self._get_access_token(
			["change_card", "create_study", "view_study", "create_participant"])["access_token"]

		"""
		Create the initial data.
		"""

		response = self.send_request("POST", "create_study", {
			"study_id": "2320",
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_study", {
			"study_id": "8190",
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "get_study_by_id", { "study_id": 2320 }, token)
		response = self.send_volatile_request("GET", "get_study_by_id", { "study_id": 8190 }, token)

		response = self.send_request("POST", "create_participant", {
			"username": "p2320"
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Fetch the card and save it as a file.
		"""
		response = self.send_request("GET", "get_card", {
			"username": "p2320",
			"temp": True
		}, token)
		self.assertEqual(response.status_code, 200)
		self.save_card(response.content, "p2320.card")
		self.start_rest("p2320.card", 3002)

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

		ports = [3002]
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

	def no_test_give_consent(self):
		"""
		Test giving basic consent.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2321")["access_token"]

		"""
		Consent cannot be given if the participant does not exist.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "p2321",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		Consent cannot be given if the study does not exist.
		"""
		token = self._get_access_token(["update_consent", "view_consent"], "p2320")["access_token"]
		response = self.send_request("POST", "give_consent", {
			"study_id": "8191",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		"""
		Test basic consent.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

	def no_test_withdraw_consent(self):
		"""
		Test withdrawing consent.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2320")["access_token"]

		"""
		Test that the basic withdrawal works.
		"""
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		Test withdrawing consent after giving it.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

	def test_check_consent(self):
		"""
		Test consent checking.
		"""

		"""
		Consent cannot be checked if the participant does not exist.
		"""
		token = self._get_access_token(["update_consent", "view_consent"], "p2321")["access_token"]

		response = self.send_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2321",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		By default, there should be no consent.
		"""

		token = self._get_access_token(["update_consent", "view_consent"], "p2320")["access_token"]
		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		There should be consent if it is given.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		"""
		When withdrawn, the consent should be revoked.
		"""

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		Consent cannot be checked if the study does not exist.
		"""
		response = self.send_request("GET", "has_consent", {
			"study_id": "8191",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_studies_by_participant", {
		"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)

		response = self.send_request("POST", "give_consent", {
			"study_id": "2320",
			"username": "p2320",
			"access_token": None,
			"port": 3002,
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "2320",
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_studies_by_participant", {
			"username": "p2320",
			"access_token": "None",
			"port": 3002,
		}, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 2)

		return

		"""
		Test the participant listing for studies.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "matt",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "matt",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": "8190",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(any(user["user_id"] == "nick" for user in body["data"]))
		self.assertTrue(any(user["user_id"] == "matt" for user in body["data"]))

		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": "2320",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(any(user["user_id"] == "nick" for user in body["data"]))

		response = self.send_request("GET", "get_participants_by_study", {
			"study_id": "2321",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)
