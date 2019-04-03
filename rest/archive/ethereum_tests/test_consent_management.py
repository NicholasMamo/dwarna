"""
Test the dynamic consent management functionality in the backend.
"""

from datetime import datetime, timedelta
import json
import os
import sys

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
	"""

	def test_give_consent(self):
		"""
		Test giving basic consent.
		"""

		clear()

		token = self._get_access_token(["create_study", "view_study", "create_participant", "update_consent", "view_consent"])["access_token"]

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
			"username": "n'\"ick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Consent cannot be given if the participant does not exist.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "nic",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		Consent cannot be given if the study does not exist.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8191",
			"username": "n'\"ick",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		"""
		Test basic consent.
		"""

		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "n'\"ick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "n'\"ick",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

	def test_withdraw_consent(self):
		"""
		Test withdrawing consent.
		"""

		clear()

		token = self._get_access_token(["create_study", "view_study", "create_participant", "update_consent", "view_consent"])["access_token"]

		"""
		Create the initial data.
		"""

		response = self.send_request("POST", "create_study", {
			"study_id": "8190",
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_volatile_request("GET", "get_study_by_id", { "study_id": 8190 }, token)

		response = self.send_request("POST", "create_participant", {
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Consent cannot be withdrawn if the participant does not exist.
		"""
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "nic",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		Consent cannot be withdrawn if the study does not exist.
		"""
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8191",
			"username": "nick",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		"""
		Test that the basic withdrawal works.
		"""
		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		Test withdrawing consent after giving it.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

	def test_check_consent(self):
		"""
		Test consent checking.
		"""

		clear()

		token = self._get_access_token(["create_study", "view_study", "update_study", "create_participant", "update_consent", "view_consent"])["access_token"]

		"""
		Create the initial data.
		"""

		response = self.send_request("POST", "create_study", {
			"study_id": "8190",
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_volatile_request("GET", "get_study_by_id", { "study_id": 8190 }, token)

		response = self.send_request("POST", "create_participant", {
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", {
			"username": "matt",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		By default, there should be no consent.
		"""
		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		There should be consent if it is given.
		"""
		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		"""
		When withdrawn, the consent should be revoked.
		"""

		response = self.send_request("POST", "withdraw_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		"""
		Consent cannot be checked if the study does not exist.
		"""
		response = self.send_request("GET", "has_consent", {
			"study_id": "8191",
			"username": "nick",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		"""
		Consent cannot be checked if the participant does not exist.
		"""
		response = self.send_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nic",
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		Test consent retrieval.
		First, create an active study, then give consent.
		Finally, update the study so it is in the past.
		"""

		response = self.send_request("POST", "create_study", {
			"study_id": "2320",
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_volatile_request("GET", "get_study_by_id", { "study_id": 2320 }, token)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "2320",
			"username": "nick",
		}, token, value=False)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertFalse(body["data"])

		response = self.send_request("POST", "give_consent", {
			"study_id": "8190",
			"username": "nick",
			"password": "pwd"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "8190",
			"username": "nick",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_studies_by_participant", {
			"username": "nick",
			"active_only": True,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)

		response = self.send_request("POST", "give_consent", {
			"study_id": "2320",
			"username": "nick",
			"password": "pwd",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "has_consent", {
			"study_id": "2320",
			"username": "nick",
		}, token, value=True)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertTrue(body["data"])

		response = self.send_request("GET", "get_studies_by_participant", {
			"username": "nick",
		}, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 2)

		response = self.send_request("POST", "update_study", {
			"study_id": "2320",
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			}, token)
		self.assertEqual(response.status_code, 200)

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
