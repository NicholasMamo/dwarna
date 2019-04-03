"""
General request exceptions that may be raised by the server.
"""

class MissingArgumentException(Exception):
	"""
	An exception that indicates that an expected parameter got no argument.
	"""

	def __init__(self, message="Missing arguments"):
		super(MissingArgumentException, self).__init__(message)

class InvalidTokenException(Exception):
	"""
	An exception that indicates that the token is invalid.
	This may be caused by a revoked or expired access token.
	"""

	def __init__(self, message="Invalid token"):
		super(InvalidTokenException, self).__init__(message)

class InsufficientScopeException(Exception):
	"""
	An exception that indicates that the access token's scope is insufficient.
	"""

	def __init__(self, message="Insufficient scope"):
		super(InsufficientScopeException, self).__init__(message)

class UnauthorizedDataAccessException(Exception):
	"""
	An exception that indicates that the user is trying to access data that is not theirs.
	"""

	def __init__(self, message="Unauthorized data access"):
		super(UnauthorizedDataAccessException, self).__init__(message)

class MethodNotAllowedException(Exception):
	"""
	An exception that indicates that the user attempted to use an API call with the incorrect method.
	"""

	def __init__(self, message="Method not allowed"):
		super(MethodNotAllowedException, self).__init__(message)
