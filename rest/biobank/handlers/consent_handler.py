"""
The route handler to handle dynamic consent-related requests.
"""

from datetime import datetime
import json
import os
import sys
import threading
import traceback

path = sys.path[0]
path = os.path.join(path, "..", "..")
if path not in sys.path:
	sys.path.insert(1, path)

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import PostgreSQLRouteHandler

class ConsentHandler(PostgreSQLRouteHandler):
	"""
	The dynamic consent handler receives and handles requests that are related to participants giving or withdrawing their consent.
	"""

	def get_attributes(self, username, attributes, *args, **kwargs):
		"""
		Get the attribute values of the participant with the given username.

		:param username: The unique username of the participant.
		:type username: str
		:param attributes: A list of attribute IDs whose values are sought.
		:type attributes: list

		:return: A response with any errors that may arise.
			The data is returned as an associative array.
			If an attribute does not have a value, None is returned instead.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			attributes = list(attributes.values()) if type(attributes) is dict else attributes
			attribute_values = dict.fromkeys(attributes, None)
			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			if not all(self._attribute_id_exists(int(attribute)) for attribute in attributes):
				raise study_exceptions.AttributeDoesNotExistException()

			for attribute_id in attributes:
				attribute_value = self._connector.select_one("""
					SELECT
						value
					FROM
						participants_attributes
					WHERE
						participant_id = '%s' AND
						attribute_id = %d
				""" % (username, int(attribute_id)))
				attribute_values[attribute_id] = attribute_value["value"] if attribute_value is not None else None

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "data": attribute_values })
		except (
				study_exceptions.AttributeDoesNotExistException,
				user_exceptions.ParticipantDoesNotExistException
			) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def give_consent(self, study_id, username, *args, **kwargs):
		"""
		Set the consent of a participant.

		:param study_id: The unique ID of the study.
		:type study_id: str
		:param username: The unique username of the participant.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)

			"""
			Consent should be the last thing that is saved.
			The others can be saved with no consequence even if the consent fails.
			"""
			thread = threading.Thread(target=self._set_consent, args=(study_id, username, True, *args), kwargs=kwargs)
			thread.start()
			self._threads.append(thread)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (
				study_exceptions.AttributeNotLinkedException,
				study_exceptions.MissingAttributesException,
				study_exceptions.StudyDoesNotExistException,
				study_exceptions.StudyExpiredException,
				user_exceptions.ParticipantDoesNotExistException
			) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			traceback.print_exc()
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def withdraw_consent(self, study_id, username, *args, **kwargs):
		"""
		Withdraw the consent of a participant.

		:param study_id: The unique ID of the study.
		:type study_id: str
		:param username: The unique username of the participant.
		:type username: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)

			thread = threading.Thread(target=self._set_consent, args=(study_id, username, False, *args), kwargs=kwargs)
			thread.start()
			self._threads.append(thread)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (
			study_exceptions.StudyDoesNotExistException,
			study_exceptions.StudyExpiredException,
			user_exceptions.ParticipantDoesNotExistException
			) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_participants_by_study(self, study_id, *args, **kwargs):
		"""
		Get a list of participant which have given their consent to the given study.

		:param study_id: The unique ID of the study.
		:type study_id: str

		:return: A response with any errors that may arise.
			The body contains the studies.
		:rtype: :class:`oauth2.web.Response`

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		"""

		response = Response()

		try:
			if not self._study_exists(study_id):
				raise study_exceptions.StudyDoesNotExistException()

			addresses = self._blockchain_connector.get_study_participants(study_id, *args, **kwargs)

			"""
			Get the information of all participants that consented to the use of their sample in the study.
			"""
			participants = self._connector.select("""
				SELECT *
				FROM
					participants
				WHERE
					address IN ('%s')
			""" % ("', '".join(addresses)))
			decrypted_data = [ self._decrypt_participant(participant) for participant in participants ]
			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "data": decrypted_data })
		except (
			study_exceptions.StudyDoesNotExistException,
		) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_studies_by_participant(self, username, *args, **kwargs):
		"""
		Get a list of studies that the participant has consented to.

		:param username: The unique username of the participant.
		:type username: str

		:return: A response with any errors that may arise.
			The body contains the studies.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)

			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			"""
			The consent status is checked later on.
			"""
			command = """
				SELECT *
				FROM studies
				"""

			rows = self._connector.select(command)

			"""
			Check the participant's consent status and only retain the study if they consented.
			"""
			studies = []
			for row in rows:
				study_id = row["study_id"]

				consent = self._blockchain_connector.has_consent(study_id, username, *args, **kwargs)
				if consent:
					studies.append(row)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({
				"data": [
					{
						"study": study,
						"researchers": self._get_study_researchers(study["study_id"]),
					} for study in studies
				],
			})
		except (
			user_exceptions.ParticipantDoesNotExistException
			) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def has_consent(self, study_id, username, *args, **kwargs):
		"""
		Check whether the participant with the given username has consented to the use of his data in the given study.

		:param study_id: The unique ID of the study.
		:type study_id: str
		:param username: The unique username of the participant.
		:type username: str

		:return: A response with any errors that may arise.
			The body contains the consent status.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)

			if not self._study_exists(study_id):
				raise study_exceptions.StudyDoesNotExistException()

			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			consent = self._blockchain_connector.has_consent(study_id, username, *args, **kwargs)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "data": consent })
		except (
			study_exceptions.StudyDoesNotExistException,
			user_exceptions.ParticipantDoesNotExistException
		) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_consent_trail(self, username, *args, **kwargs):
		"""
		Get a user's consent trail.
		This trail shows how the participant's consent for studies changed over time.

		:param username: The unique username of the participant.
		:type username: str

		:return: A response with any errors that may arise.
			The body contains the studies and the timelines.
			The two are separated from each other.
			The timeline is made up of the timestamp, and a list of consent changes separated by study IDs.
			The studies are separated by IDs, and therefore the timeline can use it as a look-up table.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		timeline = {}

		try:
			username = self._sanitize(username)

			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			"""
			The command must always check for the participant's consent status.
			"""
			command = """
				SELECT *
				FROM
					studies
				"""

			rows = self._connector.select(command)
			studies = {
				int(study["study_id"]): study for study in rows
			}

			"""
			For each study get the user's consent changes, if any.
			"""
			for row in rows:
				study_id = int(row["study_id"])

				"""
				Construct the timeline, one timestamp at a time, from the current study.
				"""
				consent_trail = self._blockchain_connector.get_consent_trail(study_id, username, *args, **kwargs)

				for (timestamp, consent) in consent_trail.items():
					timeline[timestamp] = timeline.get(timestamp, {})
					timeline[timestamp][study_id] = consent

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({
				"data":{
					"studies": studies,
					"timeline": timeline
				}
			})
		except (
			user_exceptions.ParticipantDoesNotExistException
			) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			print(e)
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def _set_consent(self, study_id, username, consent, *args, **kwargs):
		"""
		Set a user's consent to the given study.
		A consent is created if it does not exist.
		However, consent cannot be changed for inactive studies.

		:param study_id: The unique ID of the study.
		:type study_id: str
		:param username: The unique username of the participant.
		:type username: str
		:param consent: The consent status.
		:type consent: bool

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		:raises: :class:`handlers.exceptions.user_exceptions.ParticipantDoesNotExistException`
		"""

		if not self._study_exists(study_id):
			raise study_exceptions.StudyDoesNotExistException()

		if not self._participant_exists(username):
			raise user_exceptions.ParticipantDoesNotExistException()

		"""
		Set the consent accordingly.
		Do not commit transactions do not change the state of the consent.
		"""
		if (consent != self._blockchain_connector.has_consent(study_id, username, *args, **kwargs)):
			self._blockchain_connector.set_consent(study_id, username, consent, *args, **kwargs)

	def _set_attribute_value(self, attribute_id, username, value):
		"""
		Set the participant's value for the given attribute.

		:param attribute_id: The unique ID of the attribute.
		:type attribute_id: int
		:param username: The unique username of the participant.
		:type username: str
		:param value: The new value of the attribute.
		:type value: mixed

		:raises: :class:`handlers.exceptions.study_exceptions.StudyAttributeDoesNotExistException`
		:raises: :class:`handlers.exceptions.user_exceptions.ParticipantDoesNotExistException`
		"""

		if not self._attribute_id_exists(attribute_id):
			raise study_exceptions.AttributeDoesNotExistException()

		if not self._participant_exists(username):
			raise user_exceptions.ParticipantDoesNotExistException()

		if not self._connector.exists("""
			SELECT *
			FROM participants_attributes
			WHERE
				attribute_id = %d AND
				participant_id = '%s'
			""" % (attribute_id, username)):

			"""
			If an attribute's value row does not exist, it has to be created from scratch.
			"""
			self._connector.execute("""
				INSERT INTO participants_attributes(
					attribute_id, participant_id, value
				)
				VALUES(%d, '%s', '%s')
			""" % (attribute_id, username, value))
		else:
			"""
			Otherwise, just update the row for the participant.
			"""
			self._connector.execute("""
				UPDATE participants_attributes
				SET
					value = '%s'
				WHERE
					attribute_id = %d AND
					participant_id = '%s'
			""" % (value, attribute_id, username))
