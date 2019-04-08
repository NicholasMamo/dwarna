"""
Test the user management functionality in the backend.
"""

import json
import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from biobank.handlers.exceptions import general_exceptions, user_exceptions

from .environment import *

from .test import BiobankTestCase

class UserManagementTest(BiobankTestCase):
	"""
	Test the backend's user management functionality.
	"""

	def no_test_create_biobanker(self):
		"""
		Test creating a biobanker normally.
		"""

		clear()
		token = self._get_access_token(["create_biobanker"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_create_duplicate_biobanker(self):
		"""
		Test that creating a biobanker that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_biobanker"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "nick" }, token)

		response = self.send_request("POST", "create_biobanker", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerExistsException.__name__)

	def no_test_create_biobanker_with_taken_username(self):
		"""
		Test that creating a biobanker with a username that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "create_participant", { "username": "mill", "password": "pwd" }, token)

		response = self.send_request("POST", "create_biobanker", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_biobanker", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	def no_test_biobanker_sanitation(self):
		"""
		Test that the biobanker sanitation works.
		"""

		clear()
		token = self._get_access_token(["create_biobanker"])["access_token"]

		response = self.send_request("POST", "create_biobanker", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_biobanker", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_biobanker", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_biobanker", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_biobanker", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_biobanker", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_get_biobankers(self):
		"""
		Test getting a list of biobankers.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "view_biobanker"])["access_token"]

		"""
		Initially there should be no biobankers.
		"""
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create and fetch biobankers.
		"""

		response = self.send_request("POST", "create_biobanker", { "username": "luke" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "tamara" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue({ "user_id": "luke" } in body["data"])
		self.assertTrue({ "user_id": "tamara" } in body["data"])

	def no_test_get_removed_biobanker(self):
		"""
		Test getting one biobanker.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "luke" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue({ "user_id": "luke" } in body["data"])

		"""
		Remove the biobanker and try fetching them again.
		"""

		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "luke" } not in body["data"])

	def no_test_only_biobankers_returned(self):
		"""
		Test that researchers and participants are not returned with biobankers.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "view_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "create_participant", { "username": "pete", "password": "pwd" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "mariah", "password": "pwd" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "mariah" } not in body["data"])
		self.assertTrue({ "user_id": "pete" } not in body["data"])

	def no_test_remove_inexistent_biobanker(self):
		"""
		Test deleting an inexistent biobanker.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "remove_biobanker"])["access_token"]

		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerDoesNotExistException.__name__)

	def no_test_remove_biobanker(self):
		"""
		Test removing an existing biobanker.
		"""
		clear()
		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker", "create_researcher", "view_researcher", "create_participant", "view_participant"])["access_token"]
		self.send_request("POST", "create_biobanker", { "username": "nick" }, token)
		self.send_request("POST", "create_biobanker", { "username": "matt" }, token)
		self.send_request("POST", "create_participant", { "username": "pete", "password": "pwd" }, token)
		self.send_request("POST", "create_researcher", { "username": "tamara" }, token)

		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "matt" } in body["data"])

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "tamara" } in body["data"])

	def no_test_biobanker_removal_sanitation(self):
		"""
		Test that the biobanker removal sanitizes the input.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "remove_biobanker"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "jesse l'angelle" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "marie l\'angelle" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "jesse \"custer\" l'angelle" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "\\_nick" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "\\\\_nick" }, token)

		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_create_participant(self):
		"""
		Test creating a participant normally.
		"""

		clear()
		token = self._get_access_token(["create_participant"])["access_token"]
		response = self.send_request("POST", "create_participant", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_create_duplicate_participant(self):
		"""
		Test that creating a participant that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_participant"])["access_token"]
		response = self.send_request("POST", "create_participant", { "username": "nick" }, token)

		response = self.send_request("POST", "create_participant", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantExistsException.__name__)

	def no_test_create_participant_with_taken_username(self):
		"""
		Test that creating a participant with a username that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "mill", "password": "pwd" }, token)

		response = self.send_request("POST", "create_participant", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_participant", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	def no_test_participant_sanitation(self):
		"""
		Test that the participant sanitation works.
		"""

		clear()
		token = self._get_access_token(["create_participant"])["access_token"]

		response = self.send_request("POST", "create_participant", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_participant", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_participant", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_get_participants(self):
		"""
		Test getting a list of participants.
		"""

		clear()
		token = self._get_access_token(["create_participant", "view_participant"])["access_token"]

		"""
		Initially there should be no participants.
		"""
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create and fetch participants.
		"""

		response = self.send_request("POST", "create_participant", { "username": "luke" }, token)
		response = self.send_request("POST", "create_participant", { "username": "tamara" }, token)

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue({ "user_id": "luke" } in body["data"])
		self.assertTrue({ "user_id": "tamara" } in body["data"])

	def no_test_get_removed_participant(self):
		"""
		Test getting one participant.
		"""

		clear()
		token = self._get_access_token(["create_participant", "view_participant", "remove_participant"])["access_token"]
		response = self.send_request("POST", "create_participant", { "username": "luke" }, token)

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue({ "user_id": "luke" } in body["data"])

		"""
		Remove the participant and try fetching them again.
		"""

		response = self.send_request("POST", "remove_participant_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "luke" } not in body["data"])

	def no_test_only_participants_returned(self):
		"""
		Test that researchers and biobankers are not returned with participants.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant", "view_participant"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "pete", "password": "pwd" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "mariah", "password": "pwd" }, token)

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "mariah" } not in body["data"])
		self.assertTrue({ "user_id": "pete" } not in body["data"])

	def no_test_remove_inexistent_participant(self):
		"""
		Test deleting an inexistent participant.
		"""

		clear()
		token = self._get_access_token(["create_participant", "remove_participant"])["access_token"]

		response = self.send_request("POST", "remove_participant_by_username", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

	def no_test_remove_participant(self):
		"""
		Test removing an existing participant.
		"""
		clear()
		token = self._get_access_token(["create_biobanker", "view_biobanker", "create_researcher", "view_researcher", "create_participant", "view_participant", "remove_participant"])["access_token"]
		self.send_request("POST", "create_participant", { "username": "nick" }, token)
		self.send_request("POST", "create_participant", { "username": "matt" }, token)
		self.send_request("POST", "create_biobanker", { "username": "pete", "password": "pwd" }, token)
		self.send_request("POST", "create_researcher", { "username": "tamara" }, token)

		response = self.send_request("POST", "remove_participant_by_username", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "matt" } in body["data"])

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "tamara" } in body["data"])

	def test_create_researcher(self):
		"""
		Test creating a researcher normally.
		"""

		clear()
		token = self._get_access_token(["create_researcher"])["access_token"]
		response = self.send_request("POST", "create_researcher", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

	def test_create_duplicate_researcher(self):
		"""
		Test that creating a researcher that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_researcher"])["access_token"]
		response = self.send_request("POST", "create_researcher", { "username": "nick" }, token)

		response = self.send_request("POST", "create_researcher", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherExistsException.__name__)

	def test_create_researcher_with_taken_username(self):
		"""
		Test that creating a researcher with a username that already exists fails.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "create_participant", { "username": "jack" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "mill", "password": "pwd" }, token)

		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_researcher", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	def test_researcher_sanitation(self):
		"""
		Test that the researcher sanitation works.
		"""

		clear()
		token = self._get_access_token(["create_researcher"])["access_token"]

		response = self.send_request("POST", "create_researcher", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_researcher", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_researcher", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_researcher", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_researcher", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_researcher", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	def test_get_researchers(self):
		"""
		Test getting a list of researchers.
		"""

		clear()
		token = self._get_access_token(["create_researcher", "view_researcher"])["access_token"]

		"""
		Initially there should be no researchers.
		"""
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create and fetch researchers.
		"""

		response = self.send_request("POST", "create_researcher", { "username": "luke" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "tamara" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue({ "user_id": "luke" } in body["data"])
		self.assertTrue({ "user_id": "tamara" } in body["data"])

	def test_get_removed_researcher(self):
		"""
		Test getting one researcher.
		"""

		clear()
		token = self._get_access_token(["create_researcher", "view_researcher", "remove_researcher"])["access_token"]
		response = self.send_request("POST", "create_researcher", { "username": "luke" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue({ "user_id": "luke" } in body["data"])

		"""
		Remove the researcher and try fetching them again.
		"""

		response = self.send_request("POST", "remove_researcher_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "luke" } not in body["data"])

	def test_only_participants_returned(self):
		"""
		Test that biobankers and participants are not returned with researchers.
		"""

		clear()
		token = self._get_access_token(["create_biobanker", "create_researcher", "view_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "create_biobanker", { "username": "pete", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "mariah", "password": "pwd" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "mariah" } not in body["data"])
		self.assertTrue({ "user_id": "pete" } not in body["data"])
