"""
An implementation that interfaces with Hyperledger Composer's own REST API.
"""

import base64
import hashlib
import json
import os
import re
import requests
import time
import urllib
import uuid

from oauth2.web import Response

import psycopg2

from . import BlockchainAPI

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

	:ivar _host: The hostname where the Hyperledger Composer REST API is running.
	:vartype _host: str
	:ivar _default_admin_port: The default port where admin requests are made.
	:vartype _default_admin_port: int
	:ivar _default_multiuser_port: The default port where multi-user requests are made.
	:vartype _default_multiuser_port: int
	:ivar _connector: The connector that is used to access the data store.
	:vartype _connector: :class:`connection.connection.Connection`
	"""

	def __init__(self, host, default_admin_port, default_multiuser_port, connector):
		"""
		Instantiate the Hyperledger API handler with the URLs it should use.

		:param host: The hostname where the Hyperledger Composer REST API is running.
		:type host: str
		:param default_admin_port: The default port where admin requests are made.
		:type default_admin_port: int
		:param default_multiuser_port: The default port where multi-user requests are made.
		:type default_multiuser_port: int
		:param connector: The connector that is used to access the data store.
		:type connector: :class:`connection.connection.Connection`
		"""

		self._host = host
		self._default_admin_port = default_admin_port
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

		:return: The API response.
		:rtype: :class:`requests.models.Response`
		"""

		address = str(uuid.uuid4())
		response = self._create_participant(address, *args, **kwargs)
		response = self._issue_identity(address, *args, **kwargs)
		card = response.content
		self._connector.execute([
			"""
			UPDATE
				participants
			SET
				temp_card = %s, address = '%s'
			WHERE
				user_id = '%s'
			""" % (self.to_binary(card), address, username)])
		return response

	def has_card(self, username, temp, *args, **kwargs):
		"""
		Check whether the participant with the given username has a card.

		:param username: The participant's unique username.
		:type username: str
		:param temp: A boolean indicating whether the query should look at the temporary card.
			If it is set to false, the credential-ready card is queried instead.

			The boolean is actually provided as a string and converted.
		:type temp: str

		:return: A response containing a boolean indicating whether the participant has a card.
			Any errors that may arise are included.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		if (not self._card_exists(username, False, *args, **kwargs)
			and not self._card_exists(username, True, *args, **kwargs)):
			"""
			If the research partner has neither card, then re-create the participant.
			"""
			self.create_participant(username)

		temp = temp.lower() == "true"
		exists = self._card_exists(username, temp, *args, **kwargs)

		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": exists })

		return response

	def get_card(self, username, temp, *args, **kwargs):
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
		row = self._connector.select_one("""
			SELECT
				%s
			FROM
				participants
			WHERE
				user_id = '%s'
		""" % (card_name, username))

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
					public.participants
				SET
					temp_card = null
				WHERE
					user_id = '%s';
			""" % (username))

		response.status_code = 200
		response.add_header("Content-Type", "application/octet-stream")
		response.body = card_data

		return response

	def save_cred_card(self, username, card, *args, **kwargs):
		"""
		Save the user's exported Hyperledger Composer business card.
		This card is saved into the credential field.
		Later, this card can be imported back.

		The creation of the credentials card invalidates the temporary card.
		Therefore this card is set to empty.

		:param username: The participant's unique username.
		:type username: str
		:param card: The card to save.
		:type card: str

		:return: A response containing the participant's credential-ready card.
			This is not stored as a JSON string since it is a `bytes` string.
			Any errors that may arise are included.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		username = username.decode() # the username is decoded since it is coming from a binary multi-part form.

		self._connector.execute("""
			UPDATE
				public.participants
			SET
				temp_card = null,
				cred_card = %s
			WHERE
				user_id = '%s';
		""" % (self.to_binary(card), username))

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
		endpoint = f"{self._host}:{port}/api/system/identities/issue"

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
		endpoint = f"{self._host}:{port}/api/system/identities/"
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
		endpoint = f"{self._host}:{port}/api/org.consent.model.ResearchParticipant"

		response = requests.post(endpoint, data={
			"$class": "org.consent.model.ResearchParticipant",
			"participantID": username,
		})
		return response.content

	def _card_exists(self, username, temp, *args, **kwargs):
		"""
		Check whether the given card exists for the user with the given username.
		The query checks that the card is not empty.
		If it is empty, it's as if the card does not exist.

		:param username: The participant's unique username.
		:type username: str
		:param temp: A boolean indicating whether the query should look at the temporary card.
			If it is set to false, the credential-ready card is queried instead.
		:type temp: bool

		:return: A boolean indicating whether the given card exists for the user with the given username.
		:rtype: bool
		"""

		card_name = "temp" if temp else "cred"
		card_name = "%s_card" % card_name
		row = self._connector.select_one("""
			SELECT %s
			FROM participants
			WHERE user_id = '%s'
		""" % (card_name, username))

		"""
		The card exists if it is not `None`.
		"""
		card_data = row[card_name]
		return card_data is not None

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
		"""

		port = self._default_admin_port if port is None else port
		endpoint = f"{self._host}:{port}/api/org.consent.model.Study"

		response = requests.post(endpoint, data={
			"$class": "org.consent.model.Study",
			"studyID": study_id,
		})
		return response.content

	"""
	Consent.
	"""

	def set_consent(self, study_id, username, consent, access_token, port=None, *args, **kwargs):
		"""
		Set a user's consent to the given study.

		The consent ID is generated using the study's ID, the participant's username and the timestamp.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param username: The unique username of the participant.
		:type username: str
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

		address = self._get_participant_address(username)

		port = self._default_multiuser_port if port is None else port
		endpoint = f"{self._host}:{port}/api/org.consent.model.Consent"

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

	def has_consent(self, study_id, username, access_token, port=None, *args, **kwargs):
		"""
		Check whether the participant with the given username has consented to the use of his data in the given study.

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

		:return: A boolean indicating whether the participant has consented to the use of their sample in the study.
		:rtype: bool
		"""

		address = self._get_participant_address(username)
		port = self._default_multiuser_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}",
			"username": f"resource:org.consent.model.ResearchParticipant#{address}"
		}
		param_string = urllib.parse.urlencode(params)
		endpoint = f"{self._host}:{port}/api/queries/has_consent?{param_string}"
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

	def get_study_participants(self, study_id, port=None, *args, **kwargs):
		"""
		Get a list of participant addresses of participants that have consented to participate in the study with the given ID.
		The function checks only the last consent of each participant.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param port: The port to use when issuing the identity.
			By default, the request is made to the admin REST API endpoint.
		:type port: int

		:return: A list of participant addresses that have consented to participate in the study.
		:rtype: list of str
		"""

		port = self._default_admin_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}"
		}
		param_string = urllib.parse.urlencode(params)
		endpoint = f"{self._host}:{port}/api/queries/get_study_consents?{param_string}"
		response = requests.get(endpoint, headers={ })

		"""
		Sort the consent changes in descending order of timestamp to be certain of their validity.
		"""
		consent_changes = json.loads(response.content)
		consent_changes = sorted(consent_changes, key=lambda change: change['timestamp'])[::-1]

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
		address = self._get_participant_address(username)
		port = self._default_multiuser_port if port is None else port

		params = {
			"study_id": f"resource:org.consent.model.Study#{study_id}",
			"username": f"resource:org.consent.model.ResearchParticipant#{address}"
		}
		param_string = urllib.parse.urlencode(params)
		endpoint = f"{self._host}:{port}/api/queries/get_consent_trail?{param_string}"
		response = requests.get(endpoint, headers={
			"X-Access-Token": access_token
		})
		consent_changes = json.loads(response.content)
		consent_changes = {
			consent["timestamp"]: consent["status"] for consent in consent_changes
		}
		return consent_changes

	def _get_participant_address(self, username):
		"""
		Get the participant's address.

		:param username: The participant's username.
		:type username: str

		:return: The participant's address on the blockchain.
		:rtype: str
		"""

		row = self._connector.select_one("""
			SELECT
				address
			FROM
				participants
			WHERE
				user_id = '%s'
		""" % (username))
		address = row["address"]
		return address
