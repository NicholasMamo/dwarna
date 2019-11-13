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

	@BiobankTestCase.isolated_test
	def test_create_biobanker(self):
		"""
		Test creating a biobanker normally.
		"""

		token = self._get_access_token(["create_biobanker"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_create_duplicate_biobanker(self):
		"""
		Test that creating a biobanker that already exists fails.
		"""

		token = self._get_access_token(["create_biobanker"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "nick" }, token)

		response = self.send_request("POST", "biobanker", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_biobanker_with_taken_username(self):
		"""
		Test that creating a biobanker with a username that already exists fails.
		"""

		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "participant", { "username": "mill" }, token)

		response = self.send_request("POST", "biobanker", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "biobanker", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_biobanker_sanitization(self):
		"""
		Test that the biobanker sanitization works.
		"""

		token = self._get_access_token(["create_biobanker"])["access_token"]

		response = self.send_request("POST", "biobanker", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "biobanker", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "biobanker", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "biobanker", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "biobanker", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "biobanker", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_get_biobankers(self):
		"""
		Test getting a list of biobankers.
		"""

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

		response = self.send_request("POST", "biobanker", { "username": "luke" }, token)
		response = self.send_request("POST", "biobanker", { "username": "tamara" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_get_removed_biobanker(self):
		"""
		Test getting one biobanker.
		"""

		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "luke" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))

		"""
		Remove the biobanker and try fetching them again.
		"""

		response = self.send_request("DELETE", "biobanker", { "username": "luke" }, token)
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "luke" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_only_biobankers_returned(self):
		"""
		Test that researchers and participants are not returned with biobankers.
		"""

		token = self._get_access_token(["create_biobanker", "view_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "pete" }, token)
		response = self.send_request("POST", "researcher", { "username": "mariah" }, token)

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "mariah" for user in body["data"]))
		self.assertFalse(any(user["user_id"] == "pete" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_remove_inexistent_biobanker(self):
		"""
		Test deleting an inexistent biobanker.
		"""

		token = self._get_access_token(["create_biobanker", "remove_biobanker"])["access_token"]

		response = self.send_request("DELETE", "biobanker", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.BiobankerDoesNotExistException.__name__)

	@BiobankTestCase.isolated_test
	def test_remove_biobanker(self):
		"""
		Test removing an existing biobanker.
		"""
		token = self._get_access_token(["create_biobanker", "view_biobanker", "remove_biobanker", "create_researcher", "view_researcher", "create_participant", "view_participant"])["access_token"]
		self.send_request("POST", "biobanker", { "username": "nick" }, token)
		self.send_request("POST", "biobanker", { "username": "matt" }, token)
		self.send_request("POST", "participant", { "username": "pete" }, token)
		self.send_request("POST", "researcher", { "username": "tamara" }, token)

		response = self.send_request("DELETE", "biobanker", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "matt" for user in body["data"]))

		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_biobanker_removal_sanitization(self):
		"""
		Test that the biobanker removal sanitizes the input.
		"""

		token = self._get_access_token(["create_biobanker", "remove_biobanker"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "jesse l'angelle" }, token)
		response = self.send_request("POST", "biobanker", { "username": "marie l\'angelle" }, token)
		response = self.send_request("POST", "biobanker", { "username": "jesse \"custer\" l'angelle" }, token)
		response = self.send_request("POST", "biobanker", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		response = self.send_request("POST", "biobanker", { "username": "\\_nick" }, token)
		response = self.send_request("POST", "biobanker", { "username": "\\\\_nick" }, token)

		response = self.send_request("DELETE", "biobanker", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("DELETE", "biobanker", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("DELETE", "biobanker", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("DELETE", "biobanker", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("DELETE", "biobanker", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("DELETE", "biobanker", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_create_participant(self):
		"""
		Test creating a participant normally.
		"""

		token = self._get_access_token(["create_participant", "view_participant"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "")
		self.assertEqual(data["last_name"], "")
		self.assertEqual(data["email"], "")

		response = self.send_request("POST", "participant", {
			"username": "alt",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "alt@um.edu.mt"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'alt'}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "Nicholas")
		self.assertEqual(data["last_name"], "Mamo")
		self.assertEqual(data["email"], "alt@um.edu.mt")

	@BiobankTestCase.isolated_test
	def test_create_duplicate_participant(self):
		"""
		Test that creating a participant that already exists fails.
		"""

		token = self._get_access_token(["create_participant"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick" }, token)

		response = self.send_request("POST", "participant", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_participant_with_taken_username(self):
		"""
		Test that creating a participant with a username that already exists fails.
		"""

		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "researcher", { "username": "jack" }, token)
		response = self.send_request("POST", "biobanker", { "username": "mill" }, token)

		response = self.send_request("POST", "participant", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "participant", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_participant_sanitization(self):
		"""
		Test that the participant sanitization works.
		The tests include checks that the encryption does not change the value.
		"""

		token = self._get_access_token(["create_participant", "view_participant"])["access_token"]

		response = self.send_request("POST", "participant", {
			"username": "jesse l'angelle",
			"first_name": "c'thun",
			"last_name": "l'angelle",
			"email": "jesse@preacher.com"
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "jesse l'angelle"}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "c'thun")
		self.assertEqual(data["last_name"], "l'angelle")
		self.assertEqual(data["email"], "jesse@preacher.com")

		response = self.send_request("POST", "participant", {
			"username": "jesse \"custer\" l'angelle",
			"first_name": "jesse \"custer\"",
			"last_name": "l'angelle"
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "jesse \"custer\" l'angelle"}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "jesse \"custer\"")
		self.assertEqual(data["last_name"], "l'angelle")

		response = self.send_request("POST", "participant", {
			"username": "jesse \"custer\" l'angelle jr.",
			"first_name": "jesse",
			"last_name": "\"custer\" l'angelle"
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "jesse \"custer\" l'angelle jr."}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "jesse")
		self.assertEqual(data["last_name"], "\"custer\" l'angelle")

		response = self.send_request("POST", "participant", {
			"username":"theodore \\\"t.c.\\\" charles",
			"first_name": "theodore \\\"t.c.\\\" charles"
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "theodore \\\"t.c.\\\" charles"}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "theodore \\\"t.c.\\\" charles")

		response = self.send_request("POST", "participant", {
			"username":"theodore \\\"t.c.\\\" charles jr.",
			"last_name": "theodore \\\"t.c.\\\" charles"
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "theodore \\\"t.c.\\\" charles jr."}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["last_name"], "theodore \\\"t.c.\\\" charles")

		response = self.send_request("POST", "participant", { "username": "\\_nick", "first_name": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "\\_nick"}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "\\_nick")

		response = self.send_request("POST", "participant", { "username": "\\_nick jr.", "last_name": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "\\_nick jr."}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["last_name"], "\\_nick")

		response = self.send_request("POST", "participant", { "username": "\\\\_nick", "first_name": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "\\\\_nick"}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["first_name"], "\\\\_nick")

		response = self.send_request("POST", "participant", { "username": "\\\\_nick jr.", "last_name": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "participant", {'username': "\\\\_nick jr."}, token)
		data = response.json()["data"][0]
		self.assertEqual(data["last_name"], "\\\\_nick")

	@BiobankTestCase.isolated_test
	def test_update_participant(self):
		"""
		Test updating a participant normally.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "update_participant"])["access_token"]
		response = self.send_request("POST", "participant", {
			"username": "nick",
			"first_name": "",
			"last_name": "",
			"email": ""
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("", data["first_name"])
		self.assertEqual("", data["last_name"])
		self.assertEqual("", data["email"])

		"""
		Update the participant.
		"""
		response = self.send_request("PUT", "participant", {
			"username": "nick",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "nicholas.mamo@um.edu.mt"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

	@BiobankTestCase.isolated_test
	def test_update_participant_except_first_name(self):
		"""
		Test updating a participant normally without changing the first name.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "update_participant"])["access_token"]
		response = self.send_request("POST", "participant", {
			"username": "nick",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "nicholas.mamo@um.edu.mt"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

		"""
		Update the participant.
		"""
		response = self.send_request("PUT", "participant", {
			"username": "nick",
			"email": "nicholas.mamo@um.edu.mt",
			"last_name": "Tonna"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Tonna", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

	@BiobankTestCase.isolated_test
	def test_update_participant_except_last_name(self):
		"""
		Test updating a participant normally without changing the first name.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "update_participant"])["access_token"]
		response = self.send_request("POST", "participant", {
			"username": "nick",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "nicholas.mamo@um.edu.mt"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

		"""
		Update the participant.
		"""
		response = self.send_request("PUT", "participant", {
			"username": "nick",
			"email": "nicholas.mamo@um.edu.mt",
			"first_name": "Nick"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nick", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

	@BiobankTestCase.isolated_test
	def test_update_participant_except_email(self):
		"""
		Test updating a participant normally without changing the email address.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "update_participant"])["access_token"]
		response = self.send_request("POST", "participant", {
			"username": "nick",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "nicholas.mamo@um.edu.mt"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

		"""
		Update the participant.
		"""
		response = self.send_request("PUT", "participant", {
			"username": "nick",
			"first_name": "Nick"
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nick", data["first_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

	@BiobankTestCase.isolated_test
	def test_empty_update_participant(self):
		"""
		Test updating a participant without changing anything.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "update_participant"])["access_token"]
		response = self.send_request("POST", "participant", {
			"username": "nick",
			"first_name": "Nicholas",
			"last_name": "Mamo",
			"email": "nicholas.mamo@um.edu.mt" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

		"""
		Update the participant.
		"""
		response = self.send_request("PUT", "participant", {
			"username": "nick",
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "participant", {'username': 'nick'}, token)
		data = response.json()["data"][0]
		self.assertEqual("Nicholas", data["first_name"])
		self.assertEqual("Mamo", data["last_name"])
		self.assertEqual("nicholas.mamo@um.edu.mt", data["email"])

	@BiobankTestCase.isolated_test
	def test_get_participants(self):
		"""
		Test getting a list of participants.
		"""

		token = self._get_access_token(["create_participant", "view_participant"])["access_token"]

		"""
		Initially there should be no participants.
		"""
		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 0)
		self.assertEqual(body["total"], 0)

		"""
		Create and fetch participants.
		"""

		response = self.send_request("POST", "participant", { "username": "luke" }, token)
		response = self.send_request("POST", "participant", { "username": "tamara" }, token)

		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_get_removed_participant(self):
		"""
		Test getting one participant.
		"""

		token = self._get_access_token(["create_participant", "view_participant", "remove_participant"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "luke" }, token)

		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))

		"""
		Remove the participant and try fetching them again.
		"""

		response = self.send_request("DELETE", "participant", { "username": "luke" }, token)
		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "luke" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_only_participants_returned(self):
		"""
		Test that researchers and biobankers are not returned with participants.
		"""

		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant", "view_participant"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "pete" }, token)
		response = self.send_request("POST", "researcher", { "username": "mariah" }, token)

		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "mariah" for user in body["data"]))
		self.assertFalse(any(user["user_id"] == "pete" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_remove_inexistent_participant(self):
		"""
		Test deleting an inexistent participant.
		"""

		token = self._get_access_token(["create_participant", "remove_participant"])["access_token"]

		response = self.send_request("DELETE", "participant", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ParticipantDoesNotExistException.__name__)

	@BiobankTestCase.isolated_test
	def test_remove_participant(self):
		"""
		Test removing an existing participant.
		"""
		token = self._get_access_token(["create_biobanker", "view_biobanker", "create_researcher", "view_researcher", "create_participant", "view_participant", "remove_participant"])["access_token"]
		self.send_request("POST", "participant", { "username": "nick" }, token)
		self.send_request("POST", "participant", { "username": "matt" }, token)
		self.send_request("POST", "biobanker", { "username": "pete" }, token)
		self.send_request("POST", "researcher", { "username": "tamara" }, token)

		response = self.send_request("DELETE", "participant", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "matt" for user in body["data"]))

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_create_researcher(self):
		"""
		Test creating a researcher normally.
		"""

		token = self._get_access_token(["create_researcher"])["access_token"]
		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_create_duplicate_researcher(self):
		"""
		Test that creating a researcher that already exists fails.
		"""

		token = self._get_access_token(["create_researcher"])["access_token"]
		response = self.send_request("POST", "researcher", { "username": "nick" }, token)

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_researcher_with_taken_username(self):
		"""
		Test that creating a researcher with a username that already exists fails.
		"""

		token = self._get_access_token(["create_biobanker", "create_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "jack" }, token)
		response = self.send_request("POST", "biobanker", { "username": "mill" }, token)

		response = self.send_request("POST", "researcher", { "username": "jack" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

		response = self.send_request("POST", "researcher", { "username": "mill" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.UserExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_researcher_sanitization(self):
		"""
		Test that the researcher sanitization works.
		"""

		token = self._get_access_token(["create_researcher"])["access_token"]

		response = self.send_request("POST", "researcher", { "username": "jesse l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "researcher", { "username": "marie l\'angelle" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "researcher", { "username": "jesse \"custer\" l'angelle" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "researcher", { "username": "theodore \\\"t.c.\\\" charles" }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "researcher", { "username": "\\_nick" }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("POST", "researcher", { "username": "\\\\_nick" }, token)
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_get_researchers(self):
		"""
		Test getting a list of researchers.
		"""

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

		response = self.send_request("POST", "researcher", { "username": "luke" }, token)
		response = self.send_request("POST", "researcher", { "username": "tamara" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)
		self.assertEqual(body["total"], 2)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_get_removed_researcher(self):
		"""
		Test getting one researcher.
		"""

		token = self._get_access_token(["create_researcher", "view_researcher", "remove_researcher"])["access_token"]
		response = self.send_request("POST", "researcher", { "username": "luke" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)
		self.assertEqual(body["total"], 1)
		self.assertTrue(any(user["user_id"] == "luke" for user in body["data"]))

		"""
		Remove the researcher and try fetching them again.
		"""

		response = self.send_request("DELETE", "researcher", { "username": "luke" }, token)
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "luke" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_only_researchers_returned(self):
		"""
		Test that biobankers and participants are not returned with researchers.
		"""

		token = self._get_access_token(["create_biobanker", "create_researcher", "view_researcher", "create_participant"])["access_token"]
		response = self.send_request("POST", "biobanker", { "username": "pete" }, token)
		response = self.send_request("POST", "participant", { "username": "mariah" }, token)

		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertFalse(any(user["user_id"] == "mariah" for user in body["data"]))
		self.assertFalse(any(user["user_id"] == "pete" for user in body["data"]))

	@BiobankTestCase.isolated_test
	def test_remove_inexistent_researcher(self):
		"""
		Test deleting an inexistent researcher.
		"""

		token = self._get_access_token(["create_researcher", "remove_researcher"])["access_token"]

		response = self.send_request("DELETE", "researcher", { "username": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherDoesNotExistException.__name__)

	@BiobankTestCase.isolated_test
	def test_remove_researcher(self):
		"""
		Test removing an existing researcher.
		"""

		token = self._get_access_token(["create_biobanker", "view_biobanker", "create_researcher", "view_researcher", "remove_researcher", "create_participant", "view_participant"])["access_token"]
		self.send_request("POST", "researcher", { "username": "nick" }, token)
		self.send_request("POST", "researcher", { "username": "matt" }, token)
		self.send_request("POST", "biobanker", { "username": "pete" }, token)
		self.send_request("POST", "participant", { "username": "tamara" }, token)

		response = self.send_request("DELETE", "researcher", { "username": "nick" }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Ensure that the other users were not deleted.
		"""
		response = self.send_request("GET", "get_researchers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "matt" for user in body["data"]))
		self.assertFalse({ "user_id": "nick" } in body["data"])

		response = self.send_request("GET", "get_biobankers", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "pete" for user in body["data"]))

		response = self.send_request("GET", "participant", {}, token)
		body = response.json()
		self.assertTrue(any(user["user_id"] == "tamara" for user in body["data"]))
