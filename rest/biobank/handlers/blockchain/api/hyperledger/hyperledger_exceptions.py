"""
Exceptions that arise from Hyperledger tasks.
"""

class StudyAssetExistsException(Exception):
	"""
	An exception that indicates that a given study ID already belongs to an existing study.
	"""

	def __init__(self, id, message=f"Study %s already exists"):
		super(StudyAssetExistsException, self).__init__(message % id)

class UnauthorizedDataAccessException(Exception):
	"""
	An exception that indicates that a request could not be completed because the access was unauthorized.
	"""

	def __init__(self, message=f"Unauthorized access"):
		super(UnauthorizedDataAccessException, self).__init__(message)
