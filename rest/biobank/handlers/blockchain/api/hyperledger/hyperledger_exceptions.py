"""
Exceptions that arise from Hyperledger tasks.
"""

class StudyAssetExistsException(Exception):
	"""
	An exception that indicates that a given study ID already belongs to an existing study.
	"""

	def __init__(self, id, message=f"Study %s already exists"):
		super(StudyAssetExistsException, self).__init__(message % id)
