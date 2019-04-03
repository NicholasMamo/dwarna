"""
The route handler to handle researcher-related requests.
"""

import json
import traceback

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import UserHandler

class ResearcherHandler(UserHandler):
	"""
	The researcher handler class receives and handles requests that are related to researchers.
	"""

	def create_researcher(self, username, *args, **kwargs):
		"""
		Insert a researcher into the database.

		:param username: The user's username.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			if self._researcher_exists(username):
				raise user_exceptions.ResearcherExistsException()
			elif self._user_exists(username):
				raise user_exceptions.UserExistsException()

			self._connector.execute([
				"""
				INSERT INTO users (
					user_id, role)
				VALUES ('%s', '%s');""" % (username, "RESEARCHER"),
				"""
				INSERT INTO researchers (
					user_id)
				VALUES ('%s');""" % (username),
			])
			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				user_exceptions.ResearcherExistsException,
				user_exceptions.UserExistsException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def remove_researcher_by_username(self, username, *args, **kwargs):
		"""
		Remove a researcher that has the given username.

		:param username: The user's username.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			if not self._researcher_exists(username):
				raise user_exceptions.ResearcherDoesNotExistException()

			self._connector.execute([
				"""
				DELETE FROM users
				WHERE
					user_id = '%s'
					AND role = 'RESEARCHER';""" % (username),
			])
			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				user_exceptions.ResearcherDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_researchers(self, *args, **kwargs):
		"""
		Retrieve a list of all researchers.

		:return: A response containing a list of researcher objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		rows = self._connector.select("""
			SELECT *
			FROM researchers
		""")

		total = self._connector.count("""
			SELECT COUNT(*)
			FROM researchers
		""")

		response = Response()
		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": rows, "total": total })
		return response
