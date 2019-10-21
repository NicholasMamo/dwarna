"""
Exceptions about emails.
"""

class EmailDoesNotExistException(Exception):
	"""
	An exception that indicates that an email that is sought does not exist.
	"""

	def __init__(self, id, message="The email with ID %d does not exist"):
		super(EmailDoesNotExistException, self).__init__(message % id)
