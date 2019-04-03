"""
Exceptions about studies.
"""

class AttributeExistsException(Exception):
	"""
	An exception that indicates that the given attribute already exists.
	"""

	def __init__(self, message="Attribute already exists"):
		super(AttributeExistsException, self).__init__(message)

class AttributeDoesNotExistException(Exception):
	"""
	An exception that indicates that the given attribute does not exist.
	"""

	def __init__(self, message="Attribute does not exist"):
		super(AttributeDoesNotExistException, self).__init__(message)

class AttributeNotLinkedException(Exception):
	"""
	An exception that indicates that the attribute with the given ID is not linked with the study with the given ID.
	"""

	def __init__(self, message="Attribute not linked to the study"):
		super(AttributeNotLinkedException, self).__init__(message)

class MissingAttributesException(Exception):
	"""
	An exception that indicates that some of the attributes that are linked with the study are not known.
	"""

	def __init__(self, message="Some attributes are not specified"):
		super(MissingAttributesException, self).__init__(message)

class StudyExistsException(Exception):
	"""
	An exception that indicates that the given study ID already belongs to another study.
	"""

	def __init__(self, message="Study already exists"):
		super(StudyExistsException, self).__init__(message)

class StudyExpiredException(Exception):
	"""
	An exception that indicates that the study identified by the given ID is no longer active.
	"""

	def __init__(self, message="Study no longer active"):
		super(StudyExpiredException, self).__init__(message)

class StudyDoesNotExistException(Exception):
	"""
	An exception that indicates that the given study ID is not associated with any study.
	"""

	def __init__(self, message="Study does not exist"):
		super(StudyDoesNotExistException, self).__init__(message)

class InvalidStudyDurationException(Exception):
	"""
	An exception that indicates that the duration of a study is invalid.
	This typically happens because the start date is after the end date.
	"""

	def __init__(self, message="The duration of the study is invalid"):
		super(InvalidStudyDurationException, self).__init__(message)
