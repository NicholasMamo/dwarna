"""
Handles OAuth requests
"""

from wsgiref.simple_server import WSGIRequestHandler

class OAuthRequestHandler(WSGIRequestHandler):
	"""
	Request handler that enables formatting of the log messages on the console.
	This handler is used by the python-oauth2 application.
	"""

	def address_string(self):
		"""
		The string of the authority/resource server.

		:return: The name of the server
		:rtype: str
		"""

		return "server"
