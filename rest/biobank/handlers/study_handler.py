"""
The route handler to handle study-related requests.
"""

from datetime import datetime
import os
import json
import psycopg2
import sys
import threading
import traceback

path = sys.path[0]
path = os.path.join(path, "../../")
if path not in sys.path:
	sys.path.insert(1, path)

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import PostgreSQLRouteHandler

import config

class StudyHandler(PostgreSQLRouteHandler):
	"""
	The study handler class receives and handles requests that are related to studies.
	"""

	def create_study(self, study_id, name, description, homepage, researchers=None, *args, **kwargs):
		"""
		Insert a study into the database.

		:param study_id: The study's unique ID.
		:type study_id: str
		:param name: The study's name.
		:type name: str
		:param description: A short description of the study.
		:type description: str
		:param homepage: A link to the study's homepage.
		:type homepage: str
		:param researchers: A list of researchers that are participating in the study.
		:type researchers: list

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`

		:raises: :class:`handlers.exceptions.study_exceptions.StudyExistsException`
		:raises: :class:`handlers.exceptions.user_exceptions.ResearcherDoesNotExistException`
		"""

		response = Response()

		try:
			"""
			Load, parse and sanitize the study arguments.
			"""
			name, description, homepage = self._sanitize_list([ name, description, homepage ])

			researchers = [] if researchers is None else researchers
			researchers = self._sanitize_list(researchers)

			# TODO: Error-handling.
			self._blockchain_connector.create_study(study_id)

			"""
			Validate the data.
			"""
			if self._study_exists(study_id):
				raise study_exceptions.StudyExistsException()

			for researcher in researchers:
				if not self._researcher_exists(researcher):
					raise user_exceptions.ResearcherDoesNotExistException()

			"""
			Create the study.
			"""

			"""
			Add the study.
			"""
			self._connector.execute([
				"""
				INSERT INTO studies (
					study_id, name, description, homepage)
				VALUES ('%s', '%s', '%s', '%s');""" % (study_id, name, description, homepage),
			])

			"""
			Add the researchers.
			"""
			self._link_researchers(study_id, researchers)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				study_exceptions.AttributeExistsException,
				study_exceptions.StudyExistsException,
				user_exceptions.ResearcherDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def update_study(self, study_id, name, description, homepage, researchers=None, *args, **kwargs):
		"""
		Update an existing study.

		:param study_id: The study's unique ID.
		:type study_id: str
		:param name: The study's name.
		:type name: str
		:param description: A short description of the study.
		:type description: str
		:param homepage: A link to the study's homepage.
		:type homepage: str
		:param researchers: A list of researchers that are participating in the study.
		:type researchers: list

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			"""
			Load, parse and sanitize the study arguments.
			"""
			name, description, homepage = self._sanitize_list([ name, description, homepage ])

			researchers = [] if researchers is None else researchers
			researchers = self._sanitize_list(researchers)

			"""
			Validate the data.
			"""
			if not self._study_exists(study_id):
				raise study_exceptions.StudyDoesNotExistException()

			for researcher in researchers:
				if not self._researcher_exists(researcher):
					raise user_exceptions.ResearcherDoesNotExistException()

			"""
			Update the study.
			"""
			self._connector.execute([
				"""
				UPDATE studies
				SET
					"name" = '%s',
					"description" = '%s',
					"homepage" = '%s'
				WHERE
					"study_id" = '%s';""" % (name, description, homepage, study_id),
			])

			"""
			Remove all linked researchers.
			Then add the new ones.
			"""
			self._unlink_researchers(study_id)
			self._link_researchers(study_id, researchers)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				study_exceptions.AttributeExistsException,
				study_exceptions.AttributeDoesNotExistException,
				study_exceptions.StudyDoesNotExistException,
				user_exceptions.ResearcherDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def remove_study(self, study_id, *args, **kwargs):
		"""
		Remove an existing study.

		:param study_id: The study's unique ID.
		:type study_id: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			"""
			Validate the data.
			"""
			if not self._study_exists(study_id):
				raise study_exceptions.StudyDoesNotExistException()

			"""
			Remove the study.
			"""
			self._connector.execute([
				"""
				DELETE FROM studies
				WHERE
					"study_id" = '%s';""" % (study_id, ),
			])

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				study_exceptions.StudyDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_studies_by_researcher(self, researcher, number=10, page=1, search="", case_sensitive=False, *args, **kwargs):
		"""
		Retrieve a list of studies.

		:param researcher: The unique ID of the researcher, only used if it is not empty.
			The studies are filtered such that only those studies in which the researcher is participating are retrieved.
		:type researcher: str
		:param number: The number of studies to retrieve.
			If a negative number is provided, all matching studies are retrieved.
		:type number: str
		:param page: The page number, used to aid in pagination.
		:type page: str
		:param search: A search string used to look up studies using their name and description.
		:type search: str
		:param case_sensitive: A boolean indicating whether the search should be case sensitive.
		:type case_sensitive: str

		:return: A response containing a list of study objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			number = int(number)
			page = max(int(page), 1)
			case_sensitive = case_sensitive == "True"

			if not self._researcher_exists(researcher):
				raise user_exceptions.ResearcherDoesNotExistException()

			query = """
				SELECT *
				FROM studies, studies_researchers
				WHERE
					(studies."name" %s '%%%s%%' OR
					studies."description" %s '%%%s%%') AND
					studies.study_id = studies_researchers.study_id AND
					studies_researchers.researcher_id = '%s'
			""" % (
				"LIKE" if case_sensitive else "ILIKE", search,
				"LIKE" if case_sensitive else "ILIKE", search,
				researcher,
			)

			if number >= 0:
				query += """
				LIMIT %d OFFSET %d""" % (
					number, number * (page - 1)
				)

			rows = self._connector.select(query)
			for row in rows:
				del row[psycopg2.extras.RealDictRow]

			total = self._connector.count("""
				SELECT COUNT(*)
				FROM studies, studies_researchers
				WHERE
					(studies."name" %s '%%%s%%' OR
					studies."description" %s '%%%s%%') AND
					studies.study_id = studies_researchers.study_id AND
					studies_researchers.researcher_id = '%s'
			""" % (
				"LIKE" if case_sensitive else "ILIKE", search,
				"LIKE" if case_sensitive else "ILIKE", search,
				researcher,
			))

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({
				"data": [
					{
						"study": study,
						"researchers": self._get_study_researchers(study["study_id"]),
					} for study in rows
				],
				"total": total,
			})
		except (user_exceptions.ResearcherDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_studies(self, number=10, page=1, search="", case_sensitive=False, active_only=False, *args, **kwargs):
		"""
		Retrieve a list of studies.

		:param number: The number of studies to retrieve.
			If a negative number is provided, all matching studies are retrieved.
		:type number: str
		:param page: The page number, used to aid in pagination.
		:type page: str
		:param search: A search string used to look up studies using their name and description.
		:type search: str
		:param case_sensitive: A boolean indicating whether the search should be case sensitive.
		:type case_sensitive: str
		:param active_only: A boolean indicating whether only active studies should be fetched.
			By default, all studies are fetched.
			In the current implementation, the parameter has no effect.
		:type active_only: bool

		:return: A response containing a list of study objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			number = int(number)
			page = max(int(page), 1)
			case_sensitive = case_sensitive == "True"

			query = """
				SELECT *
				FROM studies
				WHERE
					(studies."name" %s '%%%s%%' OR
					studies."description" %s '%%%s%%')
			""" % (
				"LIKE" if case_sensitive else "ILIKE", search,
				"LIKE" if case_sensitive else "ILIKE", search,
			)

			if number >= 0:
				query += """
				LIMIT %d OFFSET %d""" % (
					number, number * (page - 1)
				)

			rows = self._connector.select(query)

			total = self._connector.count("""
				SELECT COUNT(*)
				FROM studies
				WHERE
					(studies."name" %s '%%%s%%' OR
					studies."description" %s '%%%s%%')
			""" % (
				"LIKE" if case_sensitive else "ILIKE", search,
				"LIKE" if case_sensitive else "ILIKE", search,
			))

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({
				"data": {
					study['study_id']: {
						"study": study,
						"researchers": self._get_study_researchers(study["study_id"]),
					} for study in rows
				},
				"total": total,
			})
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_active_studies(self, number=-1, page=1, search="", case_sensitive=False, *args, **kwargs):
		"""
		Retrieve a list of studies that are active.
		This function can be used to differentiate between studies that have been retired and active ones.
		The function acts only as a wrapper to call the `get_studies` function, filtering specifically by active studies.

		:param number: The number of studies to retrieve.
			If a negative number is given, all matching studies are retrieved.
		:type number: str
		:param page: The page number, used to aid in pagination.
			If a negative number is given, no pagination is applied.
		:type page: str
		:param search: A search string used to look up studies using their name and description.
		:type search: str
		:param case_sensitive: A boolean indicating whether the search should be case sensitive.
		:type case_sensitive: str

		:return: A response containing a list of study objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		return self.get_studies(number=number, page=page, search=search, case_sensitive=case_sensitive, active_only=True)

	def get_study_by_id(self, study_id, *args, **kwargs):
		"""
		Retrieve a single study and all associated researchers and attributes.

		:param study_id: The study's unique ID.
		:type study_id: str

		:return: A response containing a list of study objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()
		try:

			if not self._study_exists(study_id):
				raise study_exceptions.StudyDoesNotExistException()

			study = self._connector.select_one("""
				SELECT *
				FROM studies
				WHERE
					"study_id" = '%s'
			""" % (study_id))

			researchers = self._get_study_researchers(study_id)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({
				"study": study,
				"researchers": researchers,
			})
			return response
		except (general_exceptions.InputException,
				study_exceptions.StudyDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def _link_researchers(self, study_id, researchers):
		"""
		Link the given researchers, identified by their username, with the study.

		:param study_id: The unique ID of the study.
		:type study_id: str
		:param researchers: The list of researchers to link with the study.
			Each researcher is represented by their username.
		:type researchers: list

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		:raises: :class:`handlers.exceptions.user_exceptions.ResearcherDoesNotExistException`
		"""

		if not self._study_exists(study_id):
			raise study_exceptions.StudyDoesNotExistException()

		if not all(self._researcher_exists(researcher) for researcher in researchers):
			raise user_exceptions.ResearcherDoesNotExistException()

		self._connector.execute([
			"""
			INSERT INTO studies_researchers(
				study_id, researcher_id)
			VALUES ('%s', '%s');""" % (study_id, researcher)
		for researcher in researchers ])

	def _unlink_researchers(self, study_id):
		"""
		Unlink all researchers associated with the study identified by the given ID.

		:param study_id: The unique ID of the study.
		:type study_id: str

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		"""

		if not self._study_exists(study_id):
			raise study_exceptions.StudyDoesNotExistException()

		self._connector.execute([
			"""
			DELETE FROM studies_researchers
			WHERE
				"study_id" = '%s'
			""" % study_id, ])
