"""
Test the study management functionality in the backend.
"""

from datetime import datetime, timedelta

import json
import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from biobank.handlers.blockchain.api.hyperledger import hyperledger_exceptions
from biobank.handlers.exceptions import general_exceptions, study_exceptions, user_exceptions
from server.exceptions import request_exceptions

from .environment import *

from .test import BiobankTestCase

class StudyManagementTest(BiobankTestCase):
	"""
	Test the study management functionality of the biobank backend.
	"""

	@BiobankTestCase.isolated_test
	def test_create_study_with_missing_arguments(self):
		"""
		Test creating a study without all the arguments.
		"""

		token = self._get_access_token(["create_study"])["access_token"]

		"""
		Test parameters.
		"""
		response = self.send_request("POST", "study", { "name": "nick" }, token)
		body = response.json()
		self.assertEqual(response.status_code, 400)
		self.assertEqual(body["exception"], request_exceptions.MissingArgumentException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_study(self):
		"""
		Normal study creation.
		"""

		token = self._get_access_token(["create_study"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_create_duplicate_study(self):
		"""
		Test creating a study that already exists.
		"""

		token = self._get_access_token(["create_study"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token, 500)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_duplicate_blockchain_study(self):
		"""
		Test creating a study that already exists in the blockchain, but not in the database.
		"""

		token = self._get_access_token(["create_study", "remove_study"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		"""
		Delete the study.
		This removes the study information from the database, but not from the blockchain.
		"""
		response = self.send_request("DELETE", "study", {
			"study_id": study_id,
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Re-create the study with the same ID.
		This ID is taken in the blockchain.
		"""
		response = self.send_volatile_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token, 500)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], hyperledger_exceptions.StudyAssetExistsException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_study_with_inexistent_researchers(self):
		"""
		Test creating studies with inexistent researchers.
		"""

		token = self._get_access_token(["create_study"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], user_exceptions.ResearcherDoesNotExistException.__name__)

	@BiobankTestCase.isolated_test
	def test_create_study_with_researchers(self):
		"""
		Test creating studies with researchers.
		"""

		token = self._get_access_token(["create_study", "create_researcher"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

	@BiobankTestCase.isolated_test
	def test_get_study_without_id(self):
		"""
		Test getting a study without providing an ID.
		"""

		token = self._get_access_token(["create_study", "view_study"])["access_token"]

		response = self.send_request("GET", "study", { }, token)
		body = response.json()
		self.assertEqual(response.status_code, 400)
		self.assertEqual(body["exception"], request_exceptions.MissingArgumentException.__name__)

	@BiobankTestCase.isolated_test
	def test_get_inexistent_study(self):
		"""
		Test getting a study that does not exist.
		"""

		token = self._get_access_token(["create_study", "view_study"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("GET", "study", { "study_id": study_id }, token)
		body = response.json()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

	@BiobankTestCase.isolated_test
	def test_get_single_study(self):
		"""
		Create sample data.
		"""

		token = self._get_access_token(["create_study", "view_study", "create_researcher"])["access_token"]
		study_id = self._generate_study_name()

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)
		response = self.send_request("POST", "study", {
			"study_id": study_id,
			"name": "ALS",
			"description": "ALS Study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill", "nick"],
		}, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)

		response = self.send_volatile_request("GET", "study", { "study_id": study_id }, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(body["study"]["study_id"], study_id)
		self.assertEqual(len(body["researchers"]), 2)

	@BiobankTestCase.isolated_test
	def test_get_list_of_studies(self):
		"""
		Test study listings.
		"""

		token = self._get_access_token(["create_study", "view_study"])["access_token"]

		study_ids = []
		for i in range(0, 12):
			study_id = self._generate_study_name()
			study_ids.append(study_id)
			response = self.send_request("POST", "study", {
				"study_id": study_id,
				"name": "Study %d" % i,
				"description": "Another study",
				"homepage": "http://um.edu.mt",
				"researchers": [],
			}, token)

		"""
		Ensure that the studies have been created.
		"""
		for study_id in study_ids:
			response = self.send_volatile_request("GET", "study", { "study_id": study_id }, token)

		response = self.send_request("GET", "get_studies", { }, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "get_active_studies", { }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Limit number.
		"""

		response = self.send_request("GET", "get_studies", { "number": 10 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 10)

		response = self.send_request("GET", "get_active_studies", { "number": 10 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 10)

		response = self.send_request("GET", "get_studies", { "number": 20 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 12)

		response = self.send_request("GET", "get_active_studies", { "number": 1 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 1)

		response = self.send_request("GET", "get_studies", { "number": -20 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 12)

		response = self.send_request("GET", "get_active_studies", { "number": -20 }, token)
		body = response.json()["data"]
		total = response.json()["total"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 12)
		self.assertEqual(total, 12)

		response = self.send_request("GET", "get_active_studies", { "number": 0 }, token)
		body = response.json()["data"]
		total = response.json()["total"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 0)
		self.assertEqual(total, 12)

	@BiobankTestCase.isolated_test
	def test_study_pagination(self):
		"""
		Test pagination of studies.
		"""

		token = self._get_access_token(["create_study", "view_study"])["access_token"]

		study_ids = []
		for i in range(0, 12):
			study_id = self._generate_study_name()
			study_ids.append(study_id)
			response = self.send_request("POST", "study", {
				"study_id": study_id,
				"name": "Study %d" % i,
				"description": "Another study",
				"homepage": "http://um.edu.mt",
				"researchers": [],
			}, token)

		"""
		Ensure that the studies have been created.
		"""
		for study_id in study_ids:
			response = self.send_volatile_request("GET", "study", { "study_id": study_id }, token)

		response = self.send_request("GET", "get_studies", { "page": 20 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_active_studies", { "number": 1, "page": 20 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_studies", { "page": 1 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 10)

		response = self.send_request("GET", "get_active_studies", { "number": 10, "page": 1 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 10)

		response = self.send_request("GET", "get_studies", { "page": 2 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 2)

		response = self.send_request("GET", "get_studies", { "page": -1 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 10)

		response = self.send_request("GET", "get_studies", { "number": 5, "page": 3 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 2)

	@BiobankTestCase.isolated_test
	def test_search_studies(self):
		"""
		Test searches for studies.
		"""

		token = self._get_access_token(["create_study", "view_study"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name()
		]

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": [],
		}, token)

		for i in range(0, 10):
			study_id = self._generate_study_name()
			study_ids.append(study_id)
			response = self.send_request("POST", "study", {
				"study_id": study_id,
				"name": "Study %d" % i,
				"description": "Another study",
				"homepage": "http://um.edu.mt",
				"researchers": [],
			}, token)

		"""
		Ensure that the studies have been created.
		"""
		for study_id in study_ids:
			response = self.send_volatile_request("GET", "study", { "study_id": study_id }, token)

		response = self.send_request("GET", "get_studies", { "search": "ALS" }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 1)
		self.assertEqual(body[study_ids[0]]["study"]["study_id"], study_ids[0])

		response = self.send_request("GET", "get_active_studies", { "search": "ALS" }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 1)
		self.assertEqual(body[study_ids[0]]["study"]["study_id"], study_ids[0])

		response = self.send_request("GET", "get_studies", { "search": "als study", "case_sensitive": False }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 1)
		self.assertEqual(body[study_ids[0]]["study"]["study_id"], study_ids[0])

		response = self.send_request("GET", "get_active_studies", { "search": "als study", "case_sensitive": False }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 1)
		self.assertEqual(body[study_ids[0]]["study"]["study_id"], study_ids[0])

		response = self.send_request("GET", "get_studies", { "search": "als study", "case_sensitive": True }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_active_studies", { "search": "als study", "case_sensitive": True }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_studies", { "search": "study", "number": 5, "page": 3 }, token)
		body = response.json()["data"]
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(body), 2)
		self.assertEqual(response.json()["total"], 12)

	@BiobankTestCase.isolated_test
	def test_get_studies_by_researcher_without_researcher(self):
		"""
		Test filtering studies by researchers without providing a researcher.
		"""

		token = self._get_access_token(["view_study"])["access_token"]

		response = self.send_request("GET", "get_studies_by_researcher", { }, token)
		self.assertEqual(response.status_code, 400)
		body = response.json()
		self.assertEqual(body["exception"], request_exceptions.MissingArgumentException.__name__)

	@BiobankTestCase.isolated_test
	def test_get_studies_by_researcher(self):
		"""
		Test filtering studies by reseachers.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name()
		]

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[2],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[2] }, token)

		"""
		Get studies normally.
		"""

		response = self.send_request("GET", "get_studies_by_researcher", { "researcher": "nick" }, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

		response = self.send_request("GET", "get_studies_by_researcher", { "researcher": "bill" }, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 3)

	@BiobankTestCase.isolated_test
	def test_limit_studies_by_researcher(self):
		"""
		Test limiting the number of studies fetched by researcher.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name()
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[2],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[2] }, token)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 2
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 1
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 3
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

	@BiobankTestCase.isolated_test
	def test_paginate_studies_by_researcher(self):
		"""
		Test paginating the results of studies filtered by researcher.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name()
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[2],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[2] }, token)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"page": 20
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 1,
			"page": 3
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"page": 1
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 2,
			"page": 1
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"number": 1,
			"page": 2
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"page": -1
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 2)

	@BiobankTestCase.isolated_test
	def test_search_studies_of_researcher(self):
		"""
		Test searching for studies to which the researcher belongs.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
			self._generate_study_name()
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[2],
			"name": "Thalassemia",
			"description": "Thalassemia study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[2] }, token)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"search": "ALS",
			"case_sensitive": False,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)
		self.assertEqual(body[0]["study"]["study_id"], study_ids[0])

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "nick",
			"search": "diabetes",
			"case_sensitive": False,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 0)

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "bill",
			"search": "diabetes",
			"case_sensitive": False,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 1)
		self.assertEqual(body[0]["study"]["study_id"], study_ids[1])

		response = self.send_request("GET", "get_studies_by_researcher", {
			"researcher": "bill",
			"search": "diabetes",
			"case_sensitive": True,
		}, token)
		self.assertEqual(response.status_code, 200)
		body = response.json()["data"]
		self.assertEqual(len(body), 0)

	@BiobankTestCase.isolated_test
	def test_update_study(self):
		"""
		Test updating a study.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)

		"""
		Test normal updating.
		"""

		response = self.send_request("PUT", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes Type I",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)
		self.assertEqual(response.status_code, 200)
		response = self.send_request("GET", "study", { "study_id": study_ids[1] }, token)
		body = response.json()["study"]
		self.assertEqual(body["name"], "Diabetes Type I")

	@BiobankTestCase.isolated_test
	def test_update_study_researchers(self):
		"""
		Test updating a study's reseachers.
		"""

		token = self._get_access_token(["create_study", "update_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)

		"""
		Test updating researchers.
		"""

		response = self.send_request("PUT", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick"],
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "study", { "study_id": study_ids[1] }, token)
		body = response.json()["researchers"]
		self.assertEqual(body[0]["user_id"], "nick")

		response = self.send_request("GET", "study", { "study_id": study_ids[0] }, token)
		body = response.json()["researchers"]
		self.assertEqual(body[0]["user_id"], "nick")
		self.assertEqual(body[1]["user_id"], "bill")

	@BiobankTestCase.isolated_test
	def test_remove_study(self):
		"""
		Test removing a study.
		"""

		token = self._get_access_token(["create_study", "update_study", "remove_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		"""
		Test normal deletion.
		"""

		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[0] }, token)
		response = self.send_volatile_request("GET", "study", { "study_id": study_ids[1] }, token)

		response = self.send_request("GET", "get_studies", { }, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 2)

	@BiobankTestCase.isolated_test
	def test_get_removed_study(self):
		"""
		Test getting a removed study.
		"""

		token = self._get_access_token(["create_study", "update_study", "remove_study", "view_study", "create_researcher"])["access_token"]
		study_ids = [
			self._generate_study_name(),
			self._generate_study_name(),
		]

		"""
		Create a few researchers and studies.
		"""

		response = self.send_request("POST", "researcher", { "username": "nick" }, token)
		response = self.send_request("POST", "researcher", { "username": "bill" }, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[0],
			"name": "ALS",
			"description": "ALS study",
			"homepage": "http://um.edu.mt",
			"researchers": ["nick", "bill"],
		}, token)

		response = self.send_request("POST", "study", {
			"study_id": study_ids[1],
			"name": "Diabetes",
			"description": "Diabetes study",
			"homepage": "http://um.edu.mt",
			"researchers": ["bill"],
		}, token)

		"""
		Test getting a deleted study.
		"""

		response = self.send_request("DELETE", "study", { "study_id": study_ids[1] }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "get_studies", { }, token)
		body = response.json()
		self.assertEqual(len(body["data"]), 1)

		response = self.send_request("GET", "study", { "study_id": study_ids[1] }, token)
		body = response.json()
		self.assertEqual(body["exception"], study_exceptions.StudyDoesNotExistException.__name__)

		response = self.send_request("GET", "study", { "study_id": study_ids[0] }, token)
		body = response.json()
		self.assertEqual(response.status_code, 200)
