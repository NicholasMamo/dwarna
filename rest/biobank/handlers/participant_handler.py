"""
The route handler to handle participant-related requests.
"""

import json
import psycopg2
import traceback

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import UserHandler

class ParticipantHandler(UserHandler):
	"""
	The participant handler class receives and handles requests that are related to participants.
	"""

	def create_participant(self, username, name="", email="", *args, **kwargs):
		"""
		Insert a participant into the database.

		:param username: The participant's username.
		:type username: str
		:param username: The participant's name.
		:type username: str
		:param username: The participant's email.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			name = self._sanitize(name)
			email = self._sanitize(email)
			if self._participant_exists(username):
				raise user_exceptions.ParticipantExistsException()
			elif self._user_exists(username):
				raise user_exceptions.UserExistsException()

			self._connector.execute([
				"""
				INSERT INTO users (
					user_id, role)
				VALUES ('%s', '%s');""" % (username, "PARTICIPANT"),
				"""
				INSERT INTO participants (
					user_id, name, email)
				VALUES ('%s', '%s', '%s');""" % (username, name, email),
			])

			# TODO: Error-handling.
			hyperledger_response = self._blockchain_connector.create_participant(username)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				user_exceptions.ParticipantExistsException,
				user_exceptions.UserExistsException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def remove_participant_by_username(self, username, *args, **kwargs):
		"""
		Remove a participant that has the given username.

		:param username: The user's username.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			self._connector.execute([
				"""
				DELETE FROM users
				WHERE
					user_id = '%s'
					AND role = 'PARTICIPANT';""" % (username),
			])
			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (general_exceptions.InputException,
				user_exceptions.ParticipantDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_participants(self, *args, **kwargs):
		"""
		Retrieve a list of all participants.

		:return: A response containing a list of participant objects and any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		rows = self._connector.select("""
			SELECT user_id, name, email
			FROM participants
		""")

		total = self._connector.count("""
			SELECT COUNT(*)
			FROM participants
		""")

		response = Response()
		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": rows, "total": total })
		return response
