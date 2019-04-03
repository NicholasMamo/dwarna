"""
Exceptions about users.
"""

class UserExistsException(Exception):
	"""
	An exception that indicates that a given username already belongs to an existing user.
	"""

	def __init__(self, message="User already exists"):
		super(UserExistsException, self).__init__(message)

class BiobankerExistsException(Exception):
	"""
	An exception that indicates that a biobanker that is being added already exists.
	"""

	def __init__(self, message="Biobanker already exists"):
		super(BiobankerExistsException, self).__init__(message)

class BiobankerDoesNotExistException(Exception):
	"""
	An exception that indicates that a biobanker that is sought does not exist.
	"""

	def __init__(self, message="Biobanker does not exist"):
		super(BiobankerDoesNotExistException, self).__init__(message)

class ParticipantExistsException(Exception):
	"""
	An exception that indicates that a participant that is being added already exists.
	"""

	def __init__(self, message="Participant already exists"):
		super(ParticipantExistsException, self).__init__(message)

class ParticipantDoesNotExistException(Exception):
	"""
	An exception that indicates that a participant that is sought does not exist.
	"""

	def __init__(self, message="Participant does not exist"):
		super(ParticipantDoesNotExistException, self).__init__(message)

class ResearcherExistsException(Exception):
	"""
	An exception that indicates that a researcher that is being added already exists.
	"""

	def __init__(self, message="Researcher already exists"):
		super(ResearcherExistsException, self).__init__(message)

class ResearcherDoesNotExistException(Exception):
	"""
	An exception that indicates that a researcher that is sought does not exist.
	"""

	def __init__(self, message="Researcher does not exist"):
		super(ResearcherDoesNotExistException, self).__init__(message)
