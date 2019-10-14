"""
Exceptions relating to the database connection.
"""

class CredentialsNotFoundException(Exception):
	"""
	An exception that indicates that the credentials to the database were not found in the .pgpass file.
	"""

	def __init__(self, database, message="The credentials to database '%s' were not found in the .pgpass file"):
		super(CredentialsNotFoundException, self).__init__(message % database)
