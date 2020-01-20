"""
An implementation that interfaces with Hyperledger Composer's own REST API.
"""

import base64
import hashlib
import json
import os
import re
import requests
import sys
import time
import urllib
import uuid

path = sys.path[0]
path = os.path.join(path, "..", "..", '..', '..')
if path not in sys.path:
	sys.path.insert(1, path)

from oauth2.web import Response

import psycopg2

from . import hyperledger_exceptions
from .. import BlockchainAPI
from config import blockchain

class HyperledgerAPI(BlockchainAPI):
	"""
	The Hyperledger API is equipped to interface with Hyperledger Composer's REST API.

	It can communicate with two REST APIs at the same time:

		#. The admin API; and
		#. The multi-user API.

	All multi-user functions require an access token to operate.
	When users authorize their profile, they get a card.
	They import the card into Hyperledger, which creates a new card with credentials.
	Users can export this card and save it to re-import it later.

	At the same time, an access token is generated for them.
	This access token allows access to this API.

	:ivar _admin_host: The hostname where the Hyperledger Composer admin REST API is running.
	:vartype _admin_host: str
	:ivar _default_admin_port: The default port where admin requests are made.
	:vartype _default_admin_port: int or None
	:ivar _multiuser_host: The hostname where the Hyperledger Composer multi-user REST API is running.
	:vartype _multiuser_host: str
	:ivar _default_multiuser_port: The default port where multi-user requests are made.
	:vartype _default_multiuser_port: int or None
	:ivar _connector: The connector that is used to access the data store.
	:vartype _connector: :class:`connection.connection.Connection`
	"""

	def __init__(self, admin_host, default_admin_port, multiuser_host, default_multiuser_port, connector):
		"""
		Instantiate the Hyperledger API handler with the URLs it should use.

		:param admin_host: The hostname where the Hyperledger Composer admin REST API is running.
		:type host: str
		:param default_admin_port: The default port where admin requests are made.
		:type default_admin_port: int or None
		:param multiuser_host: The hostname where the Hyperledger Composer multi-user REST API is running.
		:type host: str
		:param default_multiuser_port: The default port where multi-user requests are made.
		:type default_multiuser_port: int
		:param connector: The connector that is used to access the data store.
		:type connector: :class:`connection.connection.Connection`
		"""

		self._admin_host = admin_host
		self._default_admin_port = default_admin_port
		self._multiuser_host = multiuser_host
		self._default_multiuser_port = default_multiuser_port
		self._connector = connector

	"""
	Participants.
	"""

	def create_participant(self, username, *args, **kwargs):
		"""
		Create a participant on the blockchain.

		The response contains the user's card data as a `bytes` object.

		:param username: The participant's unique username.
		:type username: str

		:return: The user's address on the blockchain.
		:rtype: str
		"""

		address = str(uuid.uuid4())
		response = self._create_participant(address, *args, **kwargs)
		response = self._issue_identity(address, *args, **kwargs)
		card = response.content
		self._connector.execute([
			"""
			INSERT INTO
				participant_identities(
					participant_id, address, temp_card)
			VALUES
				('%s', '%s', %s)
			""" % (username, address, self.to_binary(card))])
		return address

	def has_card(self, username, temp, study_id, *args, **kwargs):
		"""
		Check whether the participant with the given username has a card.

		:param username: The participant's unique username.
		:type username: str
		:param temp: A boolean indicating whether the query should look at the temporary card.
					 If it is set to false, the credential-ready card is queried instead.
					 The boolean is actually provided as a string and converted.
		:type temp: str
		:param study_id: The ID of the study that is being considered.
						 Depending on the configuration, an identity will be sought for the participant used for this study.
		:type study_id: str

		:return: A response containing a boolean indicating whether the participant has a card.
			Any errors that may arise are included.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		temp = temp.lower() == "true"
		exists = self._card_exists(username, temp, study_id, *args, **kwargs)

		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": exists })

		return response

	def get_card(self, username, temp, study_id, *args, **kwargs):
		"""
		Get the given participant's network business card.

		:param username: The participant's unique username.
		:type username: str
		:param temp: A boolean indicating whether the query should look at the temporary card.
			If it is set to false, the credential-ready card is queried instead.

			The boolean is actually provided as a string and converted.
		:type temp: str

		:return: A response containing the participant's credential-ready card.
			This is not stored as a JSON string since it is a `bytes` string.
			Any errors that may arise are included.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		temp = temp.lower() == "true"
		card_name = "temp" if temp else "cred"
		card_name = "%s_card" % card_name
		query = """
			SELECT
				%s, address
			FROM
				participant_identities
			WHERE
				participant_id = '%s' AND
				%s IS NOT NULL
		""" % (card_name, username, card_name)

		rows = self._connector.select(query)

		study_participants = self.get_all_study_participants(study_id)
		participating_rows = [ row for row in rows if row['address'] in study_participants ]

		if len(participating_rows):
			"""
			Check if the participant is already participating in a study.
			This happens regardless if the server is running in single- or multi-card mode.
			If they are, re-use that same card so the consent trail remains in the same place.
			"""

			row = participating_rows[0]
		elif not blockchain.multi_card:
			if len(rows):
				"""
				If the participant never consented to participate in this study, fetch the first identity if there is one.
				"""
				row = rows[0]
			else:
				"""
				If the research partner has no cards whatsoever, then create an identity for them.
				Then, return the newly-created card.
				"""
				self.create_participant(username)
				rows = self._connector.select(query)
				row = rows[0]
		else:
			"""
			If the research partner has never consented to the study, issue a new identity.
			Then, return the newly-created card.
			"""

			address = self.create_participant(username)
			query = """
				SELECT
					temp_card, address
				FROM
					participant_identities
				WHERE
					address = '%s'
			""" % (address)
			rows = self._connector.select(query)
			row = rows[0]

			"""
			Update the card name since the temp card will be returned now.
			"""
			card_name = 'temp_card'

		"""
		The response is a :class:`memoryview` object.
		Therefore before it is returned, it is converted into a `bytes` string.
		"""

		card_data = row[card_name]
		card_data = bytes(card_data)

		if temp:
			"""
			The temporary card can only be used once.
			Therefore it should be cleared once requested.
			"""

			self._connector.execute("""
				UPDATE
					participant_identities
				SET
					temp_card = null
				WHERE
					address = '%s';
			""" % (row['address']))

		response.status_code = 200
		response.add_header("Content-Type", "application/octet-stream")
		response.body = card_data

		return response

	def save_cred_card(self, address, card, *args, **kwargs):
		"""
		Save the user's exported Hyperledger Composer business card.
		This card is saved into the credential field.
		Later, this card can be imported back.

		The creation of the credentials card invalidates the temporary card.
		Therefore this card is set to empty.

		:param address: The participant's unique UUID.
		:type address: str
		:param card: The card to save.
		:type card: str

		:return: A response containing the participant's credential-ready card.
			This is not stored as a JSON string since it is a `bytes` string.
			Any errors that may arise are included.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		address = address.decode() # the username is decoded since it is coming from a binary multi-part form.

		self._connector.execute("""
			UPDATE
				participant_identities
			SET
				temp_card = null,
				cred_card = %s
			WHERE
				address = '%s';
		""" % (self.to_binary(card), address))

		response.status_code = 200
		return response

	def _issue_identity(self, username, port=None, *args, **kwargs):
		"""
		Issue an identity for the user with the given username.

		The response contains the user's card data as a `bytes` object.

		:param username: The participant's unique username.
		:type username: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int

		:return: The API response.
		:rtype: :class:`requests.models.Response`
		"""

		port = self._default_admin_port if port is None else port
		if port is not None:
			endpoint = f"{self._admin_host}:{port}/api/system/identities/issue"
		else:
			endpoint = f"{self._admin_host}/api/system/identities/issue"

		response = requests.post(endpoint, data={
			"participant": f"org.consent.model.ResearchParticipant#{username}",
			"userID": username,
			"options": {},
		}, headers={
			"responseType": "blob"
		})
		return response

	def _revoke_identity(self, username, port=None, *args, **kwargs):
		"""
		Revoke the identity of the user with the given username.

		First, the identity ID is fetched by looking for the username.
		Then, the identity is revoked.

		:param username: The participant's unique username.
		:type username: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int

		:return: The API response.
		:rtype: :class:`requests.models.Response`
		"""

		port = self._default_admin_port if port is None else port
		if port is not None:
			endpoint = f"{self._admin_host}:{port}/api/system/identities/"
		else:
			endpoint = f"{self._admin_host}:{port}/api/system/identities/"

		response = requests.get(endpoint)
		identities = json.loads(response.content)
		identities = {
			identity["name"]: identity["identityId"] for identity in identities
		}

		endpoint = f"{self._host}:{port}/api/system/identities/{identities[username]}/revoke"
		response = requests.post(endpoint)
		return response

	def _create_participant(self, username, port=None, *args, **kwargs):
		"""
		Create the actual Hyperledger participant on the blockchain.

		The function creates the biobank participant on the blockchain.
		The response contains the card in the `content field`.

		:param username: The participant's unique username.
		:type username: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int

		:return: The API response.
		:rtype: :class:`requests.models.Response`
		"""

		port = self._default_admin_port if port is None else port
		if port is not None:
			endpoint = f"{self._admin_host}:{port}/api/org.consent.model.ResearchParticipant"
		else:
			endpoint = f"{self._admin_host}/api/org.consent.model.ResearchParticipant"

		response = requests.post(endpoint, data={
			"$class": "org.consent.model.ResearchParticipant",
			"participantID": username,
		})
		return response.content

	def _card_exists(self, username, temp, study_id=None, *args, **kwargs):
		"""
		Check whether the given card exists for the user with the given username.
		The query checks that the card is not empty.
		If it is empty, it's as if the card does not exist.

		:param username: The participant's unique username.
		:type username: str
		:param temp: A boolean indicating whether the query should look at the temporary card.
					 If it is set to false, the credential-ready card is queried instead.
		:type temp: bool
		:param study_id: The ID of the study that is being considered.
						 Depending on the configuration, an identity will be sought for the participant used for this study.
		:type study_id: str

		:return: A boolean indicating whether the given card exists for the user with the given username.
		:rtype: bool
		"""

		card_name = "temp" if temp else "cred"
		card_name = "%s_card" % card_name
		rows = self._connector.select("""
			SELECT
				address, %s
			FROM
				participant_identities
			WHERE
				participant_id = '%s'
		""" % (card_name, username))

		if not blockchain.multi_card:
			"""
			If the server is running in single card mode, the card exists if it is not `None`.
			If the participant has no identities, then obviously they have no card.
			"""
			if len(rows):
				card_data = rows[0][card_name]
				return card_data is not None
		else:
			"""
			If the server is running in multi-card mode, the card exists if the user has a card that is linked to a study.
			In other words, a card is only valid if the user has given consent to a study.
			"""
			if len(rows):
				study_participants = self.get_all_study_participants(study_id)
				valid_rows = [ row for row in rows if row['address'] in study_participants ]
				if len(valid_rows):
					card_data = valid_rows[0][card_name]
					return card_data is not None

		return False

	"""
	Studies.
	"""

	def create_study(self, study_id, port=None, *args, **kwargs):
		"""
		Create a study on the blockchain.

		:param study_id: The study's unique ID.
		:type study_id: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int

		:return: The response content.
		:rtype: dict

		:raises: :class:`biobank.handlers.blockchain.api.hyperledger.hyperledger_exceptions.StudyAssetExistsException`
		"""

		port = self._default_admin_port if port is None else port
		if port is not None:
			endpoint = f"{self._admin_host}:{port}/api/org.consent.model.Study"
		else:
			endpoint = f"{self._admin_host}/api/org.consent.model.Study"

		response = requests.post(endpoint, data={
			"$class": "org.consent.model.Study",
			"studyID": study_id,
		})
		body = response.json()
		if 'error' in body:
			if 'already exists' in body['error']['message']:
				raise hyperledger_exceptions.StudyAssetExistsException(study_id)
		return response.content

	"""
	Consent.
	"""

	def set_consent(self, study_id, address, consent, access_token, port=None, *args, **kwargs):
		"""
		Set a user's consent to the given study.

		The consent ID is generated using the study's ID, the participant's address on the blockchain and the timestamp.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param address: The unique address of the participant on the blockchain.
		:type address: str
		:param consent: The consent status.
		:type consent: bool
		:param access_token: The participant's access token.
			This is the access token that is given upon authenticating with Hyperledger Compose.
		:type access_token: strticipant's unique username.
		:type username: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the multi-user REST API endpoint.
		:type port: int
		"""

		port = self._default_multiuser_port if port is None else port
		if port is not None:
			endpoint = f"{self._multiuser_host}:{port}/api/org.consent.model.Consent"
		else:
			endpoint = f"{self._multiuser_host}/api/org.consent.model.Consent"

		timestamp = time.time()
		base_id = str(timestamp) + str(study_id) + str(address)
		id = hashlib.md5(base_id.encode("utf-8")).hexdigest()
		response = requests.post(endpoint, data={
			"$class": "org.consent.model.Consent",
			"consentID": id,
			"timestamp": timestamp,
			"status": "true" if consent else "false",
			"participant": f"org.consent.model.ResearchParticipant#{address}",
			"study": f"org.consent.model.Study#{study_id}"
		}, headers={
			"X-Access-Token": access_token
		})

		return response.content

	def has_consent(self, study_id, address, access_token, port=None, *args, **kwargs):
		"""
		Check whether the participant with the given blockchain address has consented to the use of his data in the given study.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param address: The unique address of the participant on the blockchain.
		:type address: str
		:param access_token: The participant's access token.
			This is the access token that is given upon authenticating with Hyperledger Compose.
		:type access_token: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the multi-user REST API endpoint.
		:type port: int

		:return: A boolean indicating whether the participant has consented to the use of their sample in the study.
		:rtype: bool
		"""

		port = self._default_multiuser_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}",
			"username": f"resource:org.consent.model.ResearchParticipant#{address}"
		}
		param_string = urllib.parse.urlencode(params)

		if port is not None:
			endpoint = f"{self._multiuser_host}:{port}/api/queries/has_consent?{param_string}"
		else:
			endpoint = f"{self._multiuser_host}/api/queries/has_consent?{param_string}"

		response = requests.get(endpoint, headers={
			"X-Access-Token": access_token
		})
		consent_changes = json.loads(response.content)
		return consent_changes[0]["status"] if len(consent_changes) > 0 else False

	def get_studies_by_participant(self, username, *args, **kwargs):
		"""
		Get a list of studies that the participant has consented to.

		:param username: The unique username of the participant.
		:type username: str

		:return: A list of study IDs to which the participant has consented.
		:rtype: list
		"""

		pass

	def get_all_study_participants(self, study_id, port=None, *args, **kwargs):
		"""
		Get a list of participant addresses of participants that have consented to participate in the study with the given ID.
		The list includes all research partners that have ever participated in the study.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
			The list includes all research partners that have ever participated in the study.
		:type port: int

		:return: A list of participant addresses that have consented to participate in the study.
		:rtype: list of str
		"""

		port = self._default_admin_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}"
		}
		param_string = urllib.parse.urlencode(params)

		if port is not None:
			endpoint = f"{self._admin_host}:{port}/api/queries/get_study_consents?{param_string}"
		else:
			endpoint = f"{self._admin_host}/api/queries/get_study_consents?{param_string}"

		response = requests.get(endpoint, headers={ })

		"""
		Sort the consent changes in descending order of timestamp to be certain of their validity.
		"""
		consent_changes = json.loads(response.content)
		consent_changes = sorted(consent_changes, key=lambda change: change['timestamp'])[::-1]

		"""
		In the consent asset, the research partner is stored as:

			> `resource:org.consent.model.ResearchParticipant#44383227-f8be-4c9a-bd3d-b1ec6eb0c6b2`
		"""
		address_pattern = re.compile('\#(.+?)$')
		participants = [ address_pattern.findall(consent_change['participant'])[0] for consent_change in consent_changes ]
		return list(set(participants))

	def get_study_participants(self, study_id, port=None, token=None, *args, **kwargs):
		"""
		Get a list of participant addresses of participants that have consented to participate in the study with the given ID.
		The function checks only the last consent of each participant.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int
		:param token: The access token used to make the call.
			It is used to permit admin access only to users who have the necessary privileges.
		:type token: :class:`oauth2.datatype.AccessToken`

		:return: A list of participant addresses that are currently consenting to participate in the study.
		:rtype: list of str

		:raises: :class:`biobank.handlers.blockchain.api.hyperledger.hyperledger_exceptions.UnauthorizedDataAccessException`
		"""

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}"
		}
		param_string = urllib.parse.urlencode(params)

		"""
		If no port is given, assign the port according to the user privileges.
		If a port is given and it is the admin port, check for user privileges.
		If the user does not have access to the port, revert to the multi-user port.
		"""
		from config import routes
		if port is None:
			if token is not None and routes.admin_scope in token.scopes:
				port = self._default_admin_port

				if port is not None:
					endpoint = f"{self._admin_host}:{port}/api/queries/get_study_consents?{param_string}"
				else:
					endpoint = f"{self._admin_host}/api/queries/get_study_consents?{param_string}"
			else:
				port = self._default_multiuser_port

				if port is not None:
					endpoint = f"{self._multiuser_host}:{port}/api/queries/get_study_consents?{param_string}"
				else:
					endpoint = f"{self._multiuser_host}/api/queries/get_study_consents?{param_string}"
		elif int(port) == self._default_admin_port and routes.admin_scope not in token.scopes:
			raise hyperledger_exceptions.UnauthorizedDataAccessException()

		response = requests.get(endpoint, headers={ })

		"""
		Check whether the user could access the endpoint.
		"""
		if response.status_code == 401:
			raise hyperledger_exceptions.UnauthorizedDataAccessException()

		"""
		Sort the consent changes in descending order of timestamp to be certain of their validity.
		"""
		consent_changes = json.loads(response.content)
		consent_changes = sorted(consent_changes, key=lambda change: change['timestamp'])[::-1]

		"""
		In the consent asset, the research partner is stored as:

			> `resource:org.consent.model.ResearchParticipant#44383227-f8be-4c9a-bd3d-b1ec6eb0c6b2`
		"""
		address_pattern = re.compile('\#(.+?)$')
		checked_participants, participants = [], []
		for change in consent_changes:
			"""
			Go through each consent change, skipping those of participants that already been encountered.
			In this way, if a participant most recently withdrew consent, past occurrences of them giving consent are ignored.
			If the participant has given consent and they have not been encountered before, extract their address.
			"""
			participant = change['participant']
			if change['status'] and participant not in checked_participants:
				participants.extend(address_pattern.findall(participant))

			if participant not in checked_participants:
				checked_participants.append(participant)

		return participants

	def get_consent_trail(self, study_id, username, access_token, port=None, *args, **kwargs):
		"""
		Get a user's consent trail for the one given study.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param username: The unique username of the participant.
		:type username: str
		:param access_token: The participant's access token.
			This is the access token that is given upon authenticating with Hyperledger Compose.
		:type access_token: str
		:param port: The port to use when issuing the identity.
			By default, the request is made to the multi-user REST API endpoint.
		:type port: int

		:return: A dictionary of consent changes.
			The consent changes relate the timestamp of the consent with the consent status.
		:rtype: dict
		"""
		address = self._get_participant_address(username, study_id)

		if address is None:
			return {}

		port = self._default_multiuser_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}",
			"username": f"resource:org.consent.model.ResearchParticipant#{address}"
		}
		param_string = urllib.parse.urlencode(params)

		if port is not None:
			endpoint = f"{self._multiuser_host}:{port}/api/queries/get_consent_trail?{param_string}"
		else:
			endpoint = f"{self._multiuser_host}/api/queries/get_consent_trail?{param_string}"

		response = requests.get(endpoint, headers={
			"X-Access-Token": access_token
		})
		consent_changes = json.loads(response.content)
		consent_changes = {
			consent["timestamp"]: consent["status"] for consent in consent_changes
		}
		return consent_changes

	def _get_participant_address(self, username, study_id):
		"""
		Get the participant's address.

		:param username: The participant's username.
		:type username: str
		:param study_id: The unique ID of the study.
		:type study_id: int

		:return: The participant's address on the blockchain.
		:rtype: str or None
		"""

		if not blockchain.multi_card:
			row = self._connector.select_one("""
				SELECT
					address
				FROM
					participant_identities
				WHERE
					participant_id = '%s'
			""" % (username))
		else:
			rows = self._connector.select("""
				SELECT
					address
				FROM
					participant_identities
				WHERE
					participant_id = '%s'
			""" % (username))
			study_participants = self.get_all_study_participants(study_id)
			valid_rows = [ row for row in rows if row['address'] in study_participants ]
			row = valid_rows[0] if len(valid_rows) else None

		if row is not None:
			address = row["address"]
			return address
		else:
			return None
