"""
Define the standard functions that a blockchain API should be able to handle.
"""

from abc import ABC, abstractmethod

from ...handler import PostgreSQLRouteHandler

class BlockchainAPI(PostgreSQLRouteHandler):
	"""
	Classes that inherit from the blockchain API must implement its functionality.

	The class is meant to be a skeleton of functionality that they need to provide.
	Additional blockchain-specific parameters may be passed as `args` or `kwargs`.

	The blockchain API offers three different kinds of functionality:
		#. Participant management;
		#. Study management; and
		#. Consent management.
	"""

	"""
	Participants.
	"""

	@abstractmethod
	def create_participant(self, username, *args, **kwargs):
		"""
		Create a participant on the blockchain.

		:param username: The participant's unique username.
		:type username: str
		"""

		pass

	"""
	Studies.
	"""

	@abstractmethod
	def create_study(self, study_id, *args, **kwargs):
		"""
		Create a study on the blockchain.

		:param study_id: The study's unique ID.
		:type study_id: str
		"""

		pass

	"""
	Consent.
	"""

	@abstractmethod
	def set_consent(self, study_id, username, consent, *args, **kwargs):
		"""
		Set a user's consent to the given study.
		However, consent cannot be changed for inactive studies.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param username: The unique username of the participant.
		:type username: str
		:param consent: The consent status.
		:type consent: bool
		"""

		pass

	@abstractmethod
	def has_consent(self, study_id, username, *args, **kwargs):
		"""
		Check whether the participant with the given username has consented to the use of his data in the given study.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param username: The unique username of the participant.
		:type username: str

		:return: A boolean indicating whether the participant has consented to the use of their sample in the study.
		:rtype: bool
		"""

		pass

	@abstractmethod
	def get_studies_by_participant(self, username, *args, **kwargs):
		"""
		Get a list of studies that the participant has consented to.

		:param username: The unique username of the participant.
		:type username: str

		:return: A list of study IDs to which the participant has consented.
		:rtype: list
		"""

		pass

	@abstractmethod
	def get_consent_trail(self, study_id, username, *args, **kwargs):
		"""
		Get a user's consent trail for the one given study.

		:param study_id: The unique ID of the study.
		:type study_id: int
		:param username: The unique username of the participant.
		:type username: str

		:return: A dictionary of consent changes.
			The consent changes relate the timestamp of the consent with the consent status.
		:rtype: dict
		"""

		pass
