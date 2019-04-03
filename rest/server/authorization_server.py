"""
The authorization server is responsible for giving access tokens.
"""

from oauth2 import Provider
from oauth2.web import Response

from urllib import parse

class AuthorizationServer(Provider):
	"""
	The authorization server's only responsibility is providing access tokens.
	"""

	pass
