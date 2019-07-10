"""
The route handler encapsulates the REST API.
Its job is to handle the given requests.
"""

from abc import ABC, abstractmethod
from cryptography.fernet import Fernet
from datetime import datetime

from .exceptions import general_exceptions, study_exceptions, user_exceptions

from oauth2.web import Response

import json
import os
import psycopg2
import re
import sys

path = sys.path[0]
path = os.path.join(path, "..", "..")
if path not in sys.path:
	sys.path.insert(1, path)

from config import db

class RouteHandler(ABC):
	"""
	The route handler receives request arguments and uses them to service requests.

	:cvar encrypted_attributes: The attributes that should be stored encrypted.
	:vartype encrypted_attributes: str

	:ivar _connector: The connector that is used to access the data store.
	:vartype _connector: :class:`connection.connection.Connection`
	:ivar _blockchain_connector: The connector to the blockchain.
	:vartype _blockchain_connector: :class:`biobank.blockchain.api.BlockchainAPI`
	:ivar _threads: A list of threads, shared with the :class:`async.thread_manager.ThreadManager`.
					The threads can be used to perform time-consuming operations asynchronously.
	:type _threads: list
	"""

	encrypted_attributes = ['name', 'email']

	def __init__(self, connector, blockchain_connector, threads, *args, **kwargs):
		"""
		Create the route handler, incorporating a connection with a store.
		This store can be both in memory or as a database.
		However, all route handlers need some form of connector to manage data.

		:param connector: The connector that is used to access the data store.
		:type connector: :class:`connection.connection.Connection`
		:param blockchain_connector: The connector to the blockchain.
		:type blockchain_connector: :class:`biobank.blockchain.api.BlockchainAPI`
		:param threads: A list of threads, shared with the :class:`async.thread_manager.ThreadManager`.
						The threads can be used to perform time-consuming operations asynchronously.
		:type threads: list
		"""

		self._connector = connector
		self._blockchain_connector = blockchain_connector
		self._threads = threads

	def _404_page_not_found(self, arguments):
		"""
		Page not found error.

		:param arguments: The environment arguments.
		:type arguments: list

		:return: A 404 response with an error.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()
		response.add_header("Content-Type", "application/json")
		response.status_code = 404
		response.body = json.dumps({ "error": "Page Not Found" })
		return response

	def _encrypt(self, string):
		"""
		Encrypt the given string.

		The function looks for the encryption secret in the database configuration file.

		:param string: The string to encrypt.
		:type string: str

		:return: The encrypted string.
		:rtype: str
		"""

		f = Fernet(db.encryption_secret)
		return f.encrypt(str.encode(string)).decode()

	def _decrypt(self, string):
		"""
		Decrypt the given string.

		The function looks for the encryption secret in the database configuration file.

		:param string: The string to decrypt.
		:type string: str

		:return: The decrypted string.
		:rtype: str
		"""

		f = Fernet(db.encryption_secret)
		return f.decrypt(str.encode(string)).decode()

class PostgreSQLRouteHandler(RouteHandler):
	"""
	This class is based on PostgreSQL.
	It assumes that all the data is stored in a PostgerSQL database.

	The general workflow of handlers is as follows:

	1. Create an empty response.
	2. Extract the given arguments, if any, and sanitize them.
	3. Perform any required validation, raising exceptions if anything fails.
	4. Communicate any queries with the database, if need be, and fetch a status.
	5. Set the status code and write any required output to the response body.
	"""

	def ping(self, *args, **kwargs):
		"""
		Reply to a ping to the server.
		This function always returns a success notice.
		Its purpose is to ensure that there is a link with the server.

		:return: A success response.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()
		response.status_code = 200
		return response

	"""
	General functions
	"""

	def escape_escaped(self, string):
		"""
		Escape the escape characters in the given string.

		:param string: The string to sanitize.
		:type string: str

		:return: The sanitized string.
		:rtype: str
		"""

		escape_pattern = "\\\\(.)"
		escape_pattern = re.compile(escape_pattern)
		string = escape_pattern.sub("\g<1>", string)
		return string

	def to_binary(self, byte_string):
		"""
		Convert the given byte string to a binary representation.

		:param byte_string: The byte string to convert.
		:type byte_string: byte

		:return: The binary representation as accepted by PostgreSQL.
		:rtype: str
		"""

		clean_string = psycopg2.Binary(byte_string)
		return clean_string

	def _sanitize_list(self, l, sanitize_escaped=False):
		"""
		Sanitize all the elements in the given list to be used in PostgreSQL.

		:param l: The list containing all the elements to sanitize.
		:type l: list
		:param sanitize_escaped: A boolean indicating whether escaped characters should be sanitized.
		:type sanitize_escaped: bool

		:return: A new list of sanitized strings.
		:rtype: list
		"""

		return [ self._sanitize(e, sanitize_escaped=sanitize_escaped) for e in l ]

	def _sanitize_dict(self, d, sanitize_escaped=False):
		"""
		Sanitize all the values in the given dictionary to be used in PostgreSQL.

		:param d: The dict containing all the elements to sanitize.
		:type d: dict
		:param sanitize_escaped: A boolean indicating whether escaped characters should be sanitized.
		:type sanitize_escaped: bool

		:return: A new dict with sanitized values.
		:rtype: dict
		"""

		return { k: self._sanitize(v, sanitize_escaped=sanitize_escaped) for k, v in d.items() }


	def _sanitize(self, string, sanitize_escaped=True):
		"""
		Sanitize the given string to be used in PostgreSQL.

		:param string: The string to sanitize.
		:type string: str
		:param sanitize_escaped: A boolean indicating whether escaped characters should be sanitized.
		:type sanitize_escaped: bool

		:return: The sanitized string.
		:rtype: str
		"""

		if type(string) is str:
			"""
			Remove the escape character
			"""
			if sanitize_escaped:
				self.escape_escaped(string)

			"""
			Apostrophes have to be repeated twice.
			"""
			apostrophe_pattern = "'"
			apostrophe_pattern = ("\\\\?" if sanitize_escaped else "") + apostrophe_pattern
			apostrophe_pattern = re.compile(apostrophe_pattern)
			string = apostrophe_pattern.sub("''", string)

		return string

	def _user_exists(self, username):
		"""
		Check whether a user with the given username exists.

		:param username: The user's username.
		:type username: str

		:return: A boolean indicating whether the user exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM users
			WHERE
				user_id = '%s'
			""" % (username)
		)

		return (row is not None and len(row) > 0)

	def _biobanker_exists(self, username):
		"""
		Check whether a biobanker with the given username exists.

		:param username: The biobanker's username.
		:type username: str

		:return: A boolean indicating whether the biobanker exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM biobankers
			WHERE
				user_id = '%s'
			""" % (username)
		)

		return (row is not None and len(row) > 0)

	def _participant_exists(self, username):
		"""
		Check whether a participant with the given username exists.

		:param username: The participant's username.
		:type username: str

		:return: A boolean indicating whether the participant exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM participants
			WHERE
				user_id = '%s'
			""" % (username)
		)

		return (row is not None and len(row) > 0)

	def _researcher_exists(self, username):
		"""
		Check whether a researcher with the given username exists.

		:param username: The researcher's username.
		:type username: str

		:return: A boolean indicating whether the researcher exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM researchers
			WHERE
				user_id = '%s'
			""" % (username)
		)

		return (row is not None and len(row) > 0)

	def _get_study_researchers(self, study_id):
		"""
		Get a list of researchers associated with the study identified by the given ID.

		:param study_id: The unique ID of the study.
		:type study_id: str

		:return: A list of researcher objects.
		:rtype: list

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		"""

		if not self._study_exists(study_id):
			raise study_exceptions.StudyDoesNotExistException()

		return self._connector.select("""
			SELECT researchers.*
			FROM researchers, studies_researchers
			WHERE
				studies_researchers."study_id" = '%s' AND
				studies_researchers."researcher_id" = researchers."user_id"
		""" % (study_id, ))

	def _study_exists(self, study_id):
		"""
		Check whether a study with the given ID exists.

		:param study_id: The study's ID.
		:type study_id: str

		:return: A boolean indicating whether the study exists.
		:rtype: bool
		"""

		exists = self._connector.exists("""
			SELECT *
			FROM studies
			WHERE
				study_id = '%s'
			""" % (study_id)
		)
		return exists

	def _is_study_active(self, study_id):
		"""
		Check whether the study with the given ID is active.
		A study is active if the date of execution is between its start and end dates.
		This operation is inclusive.

		:param study_id: The study's ID.
		:type study_id: str

		:return: A boolean indicating whether the study is active.
		:rtype: bool

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		"""

		row = self._connector.select_one("""
			SELECT start_date, end_date
			FROM studies
			WHERE
				study_id = '%s'
			""" % (study_id)
		)

		start_date = row["start_date"]
		end_date = row["end_date"]
		start_date = datetime(start_date.year, start_date.month, start_date.day)
		end_date = datetime(end_date.year, end_date.month, end_date.day)
		now = datetime.now()

		return start_date <= now <= end_date

	def _get_study_attributes(self, study_id):
		"""
		Get a list of attributes associated with the study identified by the given ID.

		:param study_id: The unique ID of the study.
		:type study_id: str

		:return: A list of attribute objects.
		:rtype: list

		:raises: :class:`handlers.exceptions.study_exceptions.StudyDoesNotExistException`
		"""

		if not self._study_exists(study_id):
			raise study_exceptions.StudyDoesNotExistException()

		return self._connector.select("""
			SELECT attributes.*
			FROM attributes, studies_attributes
			WHERE
				studies_attributes."study_id" = '%s' AND
				studies_attributes."attribute_id" = attributes."attribute_id"
		""" % (study_id, ))

	def _create_attribute(self, name, type, constraints=[]):
		"""
		Create an attribute.

		:param name: The attribute name.
		:type name: str
		:param type: The attribute type.
		:type type: str
		:param constraints: The different values that the attribute may take.
		:type constraints: list

		:raises: :class:`handlers.exceptions.study_exceptions.AttributeExistsException`
		"""

		if not self._attribute_exists(name, type, constraints):
			self._connector.execute([
				"""
				INSERT INTO attributes(
					name, type, constraints)
				VALUES ('%s', '%s', '%s');""" % (name, type, "{%s}" % ','.join(constraints))
			])
		else:
			raise study_exceptions.AttributeExistsException()

	def _attribute_id_exists(self, attribute_id):
		"""
		Check whether an attribute with the given ID exists.

		:param attribute_id: The attribute's unique ID.
		:type attribute_id: str

		:return: A boolean indicating whether the attribute exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM attributes
			WHERE
				attribute_id = %d
			""" % (int(attribute_id))
		)

		return (row is not None and len(row) > 0)

	def _attribute_exists(self, name, type, constraints=[]):
		"""
		Check whether an attribute with the given details exists.

		:param name: The attribute name.
		:type name: str
		:param type: The attribute type.
		:type type: str
		:param constraints: The different values that the attribute may take.
		:type constraints: list

		:return: A boolean indicating whether the attribute exists or not.
		:rtype: bool
		"""

		row = self._connector.select_one("""
			SELECT *
			FROM attributes
			WHERE
				name = '%s' AND
				type = '%s' AND
				constraints = '%s'
			""" % (name, type, "{%s}" % ','.join(constraints))
		)

		return (row is not None and len(row) > 0)

	def _get_attribute_id(self, name, type, constraints=[]):
		"""
		Get the unique ID of the attribute having the given details.

		:param name: The attribute name.
		:type name: str
		:param type: The attribute type.
		:type type: str
		:param constraints: The different values that the attribute may take.
		:type constraints: list

		:return: The unique ID of the attribute.
		:rtype: int
		"""

		attribute_id = self._connector.select_one(
			"""SELECT *
			FROM attributes
			WHERE
				name = '%s' AND
				type = '%s' AND
				constraints = '%s'
			""" % (name, type, "{%s}" % ','.join(constraints))
		)

		return attribute_id["attribute_id"]

	def _encrypt_participant(self, participant):
		"""
		Encrypt the given participant's data.

		:param participant: The participant data to encrypt.
		:type participant: dict

		:return: The same participant, but with the updated encrypted attributes.
		:rtype: dict
		"""

		encrypted = { attribute: self._encrypt(str(participant.get(attribute))) for attribute in PostgreSQLRouteHandler.encrypted_attributes }
		encrypted_participant = dict(participant)
		encrypted_participant.update(encrypted)
		return encrypted_participant

	def _decrypt_participant(self, participant):
		"""
		Decrypt the given participant's data.

		:param participant: The participant data to decrypt.
		:type participant: dict

		:return: The same participant, but with the updated decrypted attributes.
		:rtype: dict
		"""

		decrypted = { attribute: self._decrypt(participant.get(attribute)) for attribute in PostgreSQLRouteHandler.encrypted_attributes }
		decrypted_participant = dict(participant)
		decrypted_participant.update(decrypted)
		return decrypted_participant

class UserHandler(PostgreSQLRouteHandler):
	"""
	A handler that specializes in handling user requests.
	"""

	pass
