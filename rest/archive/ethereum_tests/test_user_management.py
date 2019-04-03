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

	def test_create_biobanker(self):
		"""
		Test the biobanker creation functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "create_participant", "create_researcher"])["access_token"]

		"""
		Normal creation.
		"""
		response = self.send_request("POST", "create_biobanker", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Existing biobanker creation.
		"""
		response = self.send_request("POST", "create_biobanker", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerExistsException.__name__)

		"""
		Existing user creation.
		"""
		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_participant", { "username": "mill", "password": "pwd" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		"""
		Sanitization test.
		"""
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

	def test_get_biobankers(self):
		"""
		Test the biobanker retrieval functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker", "create_participant", "create_researcher"])["access_token"]

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create the test data.
		"""
		response = self.send_request("POST", "create_biobanker", { "username": "luke" }, token)
		response = self.send_request("POST", "create_biobanker", { "username": "tamara" }, token)

		"""
		Test getting the initial biobanker.
		"""
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue({ "user_id": "luke" } in body["data"])
		self.assertTrue({ "user_id": "tamara" } in body["data"])

		"""
		Test that removed biobanker are not returned.
		"""
		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "luke" } not in body["data"])

		"""
		Test that researchers and participants are not returned with biobankers.
		"""
		response = self.send_request("POST", "create_participant", { "username": "pete", "password": "pwd" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "mariah", "password": "pwd" }, token)
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "mariah" } not in body["data"])
		self.assertTrue({ "user_id": "pete" } not in body["data"])

	def test_remove_biobanker(self):
		"""
		Test the biobanker deletion functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker", "create_participant", "view_participant", "create_researcher", "view_researcher"])["access_token"]

		"""
		Inexisting biobanker test
		"""

		response = self.send_request("POST", "remove_biobanker_by_username", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerDoesNotExistException.__name__)

		"""
		Remove an existing biobanker.
		"""
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

		"""
		Sanitization test
		"""
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

	def test_create_participant(self):
		"""
		Test the participant creation functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "create_participant", "create_researcher"])["access_token"]

		"""
		Normal creation
		"""
		response = self.send_request("POST", "create_participant", { "username": "nick", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Existing participant creation
		"""
		response = self.send_request("POST", "create_participant", { "username": "nick", "password": "pwd" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantExistsException.__name__)

		"""
		Existing user creation
		"""
		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "create_participant", { "username": "jack", "password": "pwd" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_biobanker", { "username": "mill" }, token)
		response = self.send_request("POST", "create_participant", { "username": "mill", "password": "pwd" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		"""
		Sanitization test
		"""
		response = self.send_request("POST", "create_participant", { "username": "jesse l'angelle", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "marie l\'angelle", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_participant", { "username": "jesse \"custer\" l'angelle", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "theodore \\\"t.c.\\\" charles", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "create_participant", { "username": "\\_nick", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "create_participant", { "username": "\\\\_nick", "password": "pwd" }, token)
		self.assertEqual(response.status_code, 200)

	def test_get_participants(self):
		"""
		Test the participant retrieval functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "create_participant", "view_participant", "remove_participant", "create_researcher"])["access_token"]

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create the test data.
		"""
		response = self.send_request("POST", "create_participant", { "username": "luke", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "tamara", "password": "pwd" }, token)

		"""
		Test getting the initial participants.
		"""
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

		"""
		Test that removed participants are not returned.
		"""
		response = self.send_request("POST", "remove_participant_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue(not any(user["user_id"] == "luke" for user in body["data"]))

		"""
		Test that researchers are not returned with participants.
		"""
		response = self.send_request("POST", "create_biobanker", { "username": "pete" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "mariah" }, token)
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue(not any(user["user_id"] == "pete" for user in body["data"]))
		self.assertTrue(not any(user["user_id"] == "mariah" for user in body["data"]))

	def test_remove_participant(self):
		"""
		Test the participant deletion functionality.
		"""

		clear()

		token = self._get_access_token(["create_participant", "view_participant", "remove_participant", "create_biobanker", "view_biobanker", "create_researcher", "view_researcher"])["access_token"]

		"""
		Inexisting participant test
		"""

		response = self.send_request("POST", "remove_participant_by_username", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

		"""
		Remove existing parti
		"""
		self.send_request("POST", "create_participant", { "username": "nick", "password": "pwd" }, token)
		self.send_request("POST", "create_participant", { "username": "matt", "password": "pwd" }, token)
		self.send_request("POST", "create_biobanker", { "username": "pete" }, token)
		self.send_request("POST", "create_researcher", { "username": "tamara" }, token)

		response = self.send_request("POST", "remove_participant_by_username", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "matt" for user in body["data"]))

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

		"""
		Sanitization test
		"""
		response = self.send_request("POST", "create_participant", { "username": "jesse l'angelle", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "marie l\'angelle", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "jesse \"custer\" l'angelle", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "theodore \\\"t.c.\\\" charles", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "\\_nick", "password": "pwd" }, token)
		response = self.send_request("POST", "create_participant", { "username": "\\\\_nick", "password": "pwd" }, token)

		response = self.send_request("POST", "remove_participant_by_username", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_participant_by_username", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_participant_by_username", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_participant_by_username", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_participant_by_username", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_participant_by_username", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	def no_test_create_researcher(self):
		"""
		Test the researcher creation functionality.
		"""

		clear()

		token = self._get_access_token(["create_biobanker", "create_participant", "create_researcher"])["access_token"]

		"""
		Normal creation
		"""
		response = self.send_request("POST", "create_researcher", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Existing researcher creation
		"""
		response = self.send_request("POST", "create_researcher", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherExistsException.__name__)

		"""
		Existing user creation
		"""
		response = self.send_request("POST", "create_participant", { "username": "jack" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "create_biobanker", { "username": "mill" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		"""
		Sanitization test
		"""
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

	def no_test_get_researchers(self):
		"""
		Test the researcher retrieval functionality.
		"""

		clear()

		token = self._get_access_token(["create_researcher", "view_researcher", "remove_researcher", "create_biobanker", "create_participant"])["access_token"]

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create the test data.
		"""
		response = self.send_request("POST", "create_researcher", { "username": "luke" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "tamara" }, token)

		"""
		Test getting the initial participants.
		"""
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue({ "user_id": "luke" } in body["data"])
		self.assertTrue({ "user_id": "tamara" } in body["data"])

		"""
		Test that removed participants are not returned.
		"""
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "luke" }, token)
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "luke" } not in body["data"])

		"""
		Test that researchers are not returned with participants.
		"""
		response = self.send_request("POST", "create_biobanker", { "username": "pete" }, token)
		response = self.send_request("POST", "create_participant", { "username": "mariah" }, token)
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "pete" } not in body["data"])
		self.assertTrue({ "user_id": "mariah" } not in body["data"])

	def no_test_remove_researcher(self):
		"""
		Test the researcher deletion functionality.
		"""

		clear()

		token = self._get_access_token(["create_researcher", "view_researcher", "remove_researcher", "create_biobanker", "view_biobanker", "create_participant", "view_participant"])["access_token"]

		"""
		Inexisting researcher test
		"""

		response = self.send_request("POST", "remove_researcher_by_username", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherDoesNotExistException.__name__)

		"""
		Remove existing researcher
		"""
		self.send_request("POST", "create_researcher", { "username": "nick" }, token)
		self.send_request("POST", "create_researcher", { "username": "matt" }, token)
		self.send_request("POST", "create_biobanker", { "username": "pete" }, token)
		self.send_request("POST", "create_participant", { "username": "tamara" }, token)

		response = self.send_request("POST", "remove_researcher_by_username", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "matt" } in body["data"])

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "pete" } in body["data"])

		response = self.send_request("GET", "get_participants", {}, token)
		body = response.json()
		self.assertTrue({ "user_id": "tamara" } in body["data"])

		"""
		Sanitization test
		"""
		response = self.send_request("POST", "create_researcher", { "username": "jesse l'angelle" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "marie l\'angelle" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "jesse \"custer\" l'angelle" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "\\_nick" }, token)
		response = self.send_request("POST", "create_researcher", { "username": "\\\\_nick" }, token)

		response = self.send_request("POST", "remove_researcher_by_username", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "remove_researcher_by_username", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
