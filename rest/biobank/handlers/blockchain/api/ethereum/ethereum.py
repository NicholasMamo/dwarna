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
import web3
from eth_account import Account
import secrets
import json
from . import ethereum_exceptions

with open('biobank/handlers/blockchain/api/ethereum/contract.json') as f:
   contract_details = json.load(f)

w3= web3.Web3(web3.HTTPProvider('http://127.0.0.1:8543'))

from oauth2.web import Response

from .. import BlockchainAPI
from config import blockchain

import psycopg2

class EthereumAPI(BlockchainAPI):
	"""
	The Hyperledger API is equipped to interface with Hyperledger Composer's REST API.

	It can communicate with two REST APIs at the same time:

		#. The admin API; and
		#. The multi-user API.

	All multi-user functions require an access token to operate
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

	def __init__(self, admin_host, default_admin_port, multiuser_host, default_multiuser_port, connector, contract_address):
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

		self._private_key = "d2c1bcd72e0151f0bb53aa54f2510ee053e354bc6460c5610f24ea9db71c2ee0"
		self._contract = w3.eth.contract(address=contract_address, abi=contract_details["abi"])
		self._account = w3.eth.account.privateKeyToAccount(self._private_key)

	def _get_tx_params(self):
		"""
		Generates the transaction parameters

		The response contains the transaction parameters used to build the transaction.

		:return: The transaction parameters
		:rtype: json {"from": str, "chainId": int, "gas": int, "gasPrice": int(wei), "nonce": int}
		"""
		nonce = w3.eth.getTransactionCount(self._account.address)
		return {"from": self._account.address, "chainId": 101010, "gas": 200000, "gasPrice": w3.toWei('1', 'gwei'), "nonce": nonce}

	def _sign_tx(self, tx):
		"""
		Signs a transaction and sends it to the blockchain.

		:param tx: The transaction to sign
		:type username: web3.py transaction
		"""
		signed_txn = w3.eth.account.signTransaction(tx, private_key=self._private_key)
		result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
		print("tx hash", result.hex())

		tx = None
		tx_blk_num = None       
		while tx_blk_num == None:
			tx = w3.eth.get_transaction(result)
			tx_blk_num = tx.blockNumber
			time.sleep(0.5)
				
		replay_tx = {
			'to': tx['to'],
			'from': tx['from'],
			'value': tx['value'],
			'data': tx['input'],
		}

		try:
			w3.eth.call(replay_tx, tx.blockNumber - 1)
			return result.hex()
		except Exception as e: 
			return str(e)


	"""
	Participants.
	"""

	def _generate_key_pair(self):
		"""
		Generates an address and the corresponding private key

		The response contains the private key and the public key (address) of the new user

		:return: The private key of the user and the public key of the user
		:rtype: str, str
		"""
		priv = secrets.token_hex(32)
		private_key = "0x" + priv
		acct = Account.from_key(private_key)
		return private_key, acct.address

	def create_participant(self, username, *args, **kwargs):
		"""
		Create a participant on the blockchain.

		The response contains the user's card data as a `bytes` object.

		:param username: The participant's unique username.
		:type username: str

		:return: The user's address on the blockchain.
		:rtype: str
		"""

		private_key, address = self._generate_key_pair()

		query = """
			INSERT INTO
				participant_identities_eth(
					participant_id, address)
			VALUES
				('%s', '%s')
			""" % (username, address)
		self._connector.execute([
			"""
			INSERT INTO
				participant_identities_eth(
					participant_id, address, private_key)
			VALUES
				('%s', '%s', '%s')
			""" % (username, address, private_key)])
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

		exists = self._card_exists(username, False, study_id, *args, **kwargs)

		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": exists })

		return response

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

		rows = self._connector.select("""
			SELECT
				address, private_key
			FROM
				participant_identities_eth
			WHERE
				participant_id = '%s'
		""" % username)

		if not blockchain.multi_card:
			"""
			If the server is running in single card mode, the card exists if it is not `None`.
			If the participant has no identities, then obviously they have no card.
			"""
			if len(rows):
				card_data = rows[0]["private_key"]
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
					card_data = valid_rows[0]["private_key"]
					return card_data is not None

		return False

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

		query = """
			SELECT
				private_key, address
			FROM
				participant_identities_eth
			WHERE
				participant_id = '%s' AND
				private_key IS NOT NULL
		""" % username

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
			
			if len(rows) < 1:
				address = self.create_participant(username)

				query = """
					SELECT
						private_key, address
					FROM
						participant_identities_eth
					WHERE
						address = '%s'
				""" % (address)
				rows = self._connector.select(query)

			row = rows[0]

		"""
		The response is a :class:`memoryview` object.
		Therefore before it is returned, it is converted into a `bytes` string.
		"""

		print("Row", row);
		card_data = row["private_key"]
		address = row["address"]
		card_data = bytes(address, "ascii")

		response.status_code = 200
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

		response.status_code = 200
		return response


	# """
	# Studies.
	# """

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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.CreateStudyFailedException`
		"""

		tx_params = self._get_tx_params()
		transaction = self._contract.functions.createStudy(study_id).buildTransaction(tx_params)
		#sign tx
		response = self._sign_tx(transaction)

		if "execution reverted" in response:
			raise ethereum_exceptions.CreateStudyFailedException(ethereum_exceptions.get_error_msg(response))

		return response

	def set_consent(self, study_id, address, consent, port=None, *args, **kwargs):
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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.AddConsentToStudyFailedException`
		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.WithdrawConsentFromStudyFailedException`
		"""

		tx_params = self._get_tx_params()
		#if consent, add consent
		if consent:
			transaction = self._contract.functions.addConsentToStudy(study_id, address).buildTransaction(tx_params)
			response = self._sign_tx(transaction)
			if type(response) == str and "execution reverted" in response:
				raise ethereum_exceptions.AddConsentToStudyFailedException(ethereum_exceptions.get_error_msg(response))
		#otherwise, withdraw consent
		else:
			transaction = self._contract.functions.withdrawConsentFromStudy(study_id, address).buildTransaction(tx_params)
			response = self._sign_tx(transaction)
			if type(response) == str and "execution reverted" in str(response):
				raise ethereum_exceptions.WithdrawConsentFromStudyFailedException(ethereum_exceptions.get_error_msg(response))

		return response

	def has_consent(self, study_id, address, access_token=None, port=None, *args, **kwargs):
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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.HasConsentedFailedException`
		"""
		print("Checking consent for", address)

		#check if consented
		response = self._contract.functions.hasConsented(study_id, address).call()
		if type(response) == str and "execution reverted" in str(response):
			raise ethereum_exceptions.HasConsentedFailedException(ethereum_exceptions.get_error_msg(response))

		return response

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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.GetAllStudyParticipantsFailedException`
		"""

		try: 
			response = self._contract.functions.getAllStudyParticipants(study_id).call()
			return response
		except Exception as e: 
			raise ethereum_exceptions.GetAllStudyParticipantsFailedException(ethereum_exceptions.get_error_msg(str(e)))

	def get_study_participants(self, study_id, port=None, *args, **kwargs):
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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.GetConsentingParticipantsFailedException`
		"""

		try: 
			response = self._contract.functions.getConsentingParticipants(study_id).call()
			return response
		except Exception as e: 
			raise ethereum_exceptions.GetConsentingParticipantsFailedException(ethereum_exceptions.get_error_msg(str(e)))

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

		:raises: :class:`biobank.handlers.blockchain.api.ethereum.ethereum_exceptions.GetConsentTrailFailedException`
		"""
		
		address = self._get_participant_address(username, study_id)
		print("Address: ",address)
		try: 
			response = self._contract.functions.getConsentTrail(study_id, address).call()
			print("Consent trail response", response)
		except Exception as e: 
			print("Get consent trail failed", str(e));
			raise ethereum_exceptions.GetConsentTrailFailedException(ethereum_exceptions.get_error_msg(str(e)))

		consent_changes = {}
		#for each consent in trail
		for i in range(len(response[0])):
			consent_changes[response[0][i]] = response[1][i]

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
					participant_identities_eth
				WHERE
					participant_id = '%s'
			""" % (username))
		else:
			rows = self._connector.select("""
				SELECT
					address
				FROM
					participant_identities_eth
				WHERE
					participant_id = '%s'
			""" % (username))
			study_participants = self.get_all_study_participants(study_id)
			row = rows[0]

		if row is not None:
			address = row["address"]
			return address
		else:
			return None
