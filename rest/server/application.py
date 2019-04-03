"""
The application that handles requests
"""

from oauth2.web.wsgi import Application, Request

class OAuthApplication(Application):
	"""
	The application that handles incoming requests.
	This is built on the default :class:`oauth2.web.wsgi.Application`
	"""

	def __init__(self, resource_provider, authorization_server, authorize_uri="/authorize", env_vars=None,
				 request_class=Request, token_uri="/token"):
		"""
		Create the application.

		:param resource_provider: The resource server.
		:type resource_provider: :class:`server.ResourceServer`
		:param authorization_server: The authorization server.
		:type authorization_server: :class:`server.AuthorizationServer`
		:param authorize_uri: The link that is used to authorize users, used only in the classic three-legged authentication grant flow.
		:type authorize_uri: str
		:param env_vars: Any known environment variables.
		:type env_vars: list
		:param request_class: The request class.
		:type request_class: :class:`oauth2.web.wsgi.Request`
		"""

		super(OAuthApplication, self).__init__(resource_provider, authorize_uri, env_vars, request_class, token_uri)

		self.authorization_server = authorization_server

		"""
		Add some status codes that are not included by default.
		"""
		self.HTTP_CODES.update({
			403: "403 Forbidden",
			405: "405 Method Not Allowed",
			500: "500 Internal Server Error",
		})

	def __call__(self, env, start_response):
		"""
		A request that needs to be serviced invokes the application.

		:param env: The list of environment variables.
		:type env: list
		:param start_response: The handler that starts building the response.
		:type start_response: function
		:return: A list containing the response body, encoded using UTF-8.
		:rtype: list
		"""

		environ = {}

		if isinstance(self.env_vars, list):
			for varname in self.env_vars:
				if varname in env:
					environ[varname] = env[varname]

		"""
		If the request needs a token or some form of authorization, send the request to the authorization server.
		Otherwise, the resource provider handles the request.
		"""
		request = self.request_class(env)
		if env.get("PATH_INFO") in [self.authorize_uri, self.token_uri]:
			response = self.authorization_server.dispatch(request, environ)
		else:
			response = self.provider.handle_request(request, env)

		start_response(self.HTTP_CODES[response.status_code],
					   list(response.headers.items()))

		if type(response.body) is not bytes:
			return [response.body.encode('utf-8')]
		else:
			return [response.body]
