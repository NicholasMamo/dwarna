"""
The resource server is responsible for validating and processing requests.
More information, including status codes: https://www.oauth.com/oauth2-servers/the-resource-server/
"""

import json
import os
import re
import sys
import traceback

from requests_toolbelt.multipart import decoder

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

from oauth2 import error
from oauth2 import Provider
from oauth2.web import Response

from urllib import parse

from .exceptions import request_exceptions
from biobank.handlers.handler import PostgreSQLRouteHandler

class ResourceServer(Provider):
	"""
	The resource server receives requests from an application and services them.
	An important component of the resource server is its validation of requests.

	:ivar _routes: A list of routes, associated handles and scopes
	:vartype _routes: dict of dicts
	:ivar _route_handlers: The objects that are used to handle requests for different routes.
	:vartype _route_handlers: dict
	"""

	def __init__(self, access_token_store, auth_code_store, client_store, token_generator,
		routes, route_handlers):
		"""
		Create the resource server based on :class:`oauth2.Provider`.
		The first arguments should be the :class:`oauth2.Provider`'s.

		The resource server receives a list of routes that it can handle.
		Routes are dictionaries, where the keys are the paths.
		The value is another dictionary of the form:

		.. code-block:: python

		   {
		   	"/create_participant": {
		   		"handler": handler_class,
				"function": create_participant,
		   		"scopes": ['create_participant'],
				"parameters": ['username'],
				"method": ["POST"],
				"self_only": True
		   	}
		   }

		Associated with each route is the function that handles it.
		Each route also has a list of scopes that restrict access to protected resources.
		Moreover, to protect against erroneous requests, the method is linked with the API endpoint as well.

		The `self_only` attribute is optional.
		When set to `True`, it restricts participants to access only their own data.

		The provided route handler contains the functions that handle each route.

		:param access_token_store: Store for all access tokens.
		:type access_token_store: :class:`oauth2.store.AccessTokenStore`
		:param auth_token_store: Store for all authorization tokens.
		:type auth_token_store: :class:`oauth2.store.AccessTokenStore`
		:param client_store: Store for the known clients.
		:type client_store: :class:`oauth2.store.memory.ClientStore`
		:param token_generator: Generates new authorization and access tokens.
		:type token_generator: :class:`oauth2.tokengenerator.TokenGenerator`
		:param routes: A list of routes, associated handles and scopes
		:type routes: dict of dicts
		:param route_handlers: The objects that are used to handle requests for different routes.
		:type route_handlers: dict
		"""

		super(ResourceServer, self).__init__(access_token_store, auth_code_store, client_store, token_generator)

		self._routes = routes
		self._route_handlers = route_handlers

	def handle_request(self, request, env):
		"""
		Handle a request that has been received.
		The request information is stored in the environment variable.

		Error codes from `Mozilla <https://www.oauth.com/oauth2-servers/the-resource-server/>`_.

		:param request: The original request. This includes the headers.
		:type request: :class:`oauth2.web.wsgi.Request`
		:param env: The request environment.
		:type env: dict

		:return: A response.
		:rtype: :class:`oauth2.web.Response`
		"""

		path, method = env.get("PATH_INFO"), env.get("REQUEST_METHOD").upper()
		resource = self._routes.get(path, {}) # Get the route
		route = resource.get(method, {}) # Get the actual route handler according to the method

		api_handler = route.get("handler", list(self._route_handlers.keys())[0])
		api_function = route.get("function", api_handler._404_page_not_found) # If the route function is not found, return a 404 error
		api_scopes = list(route.get("scopes", [])) # Get the scopes, or permissions, that are requirerd by the API endpoint
		api_method = list(route.get("method", [])) # Get the type of method that is expected by the API endpoint
		api_self_only = route.get("self_only", False) # Check whether the call allows users access only to their own data
		required_parameters = route.get("parameters", [])

		response = Response()
		try:
			access_token = request.header("Authorization")
			token = self.access_token_store.fetch_by_token(access_token) # Fetch the token

			if not self._is_authorized(token, api_scopes):
				raise request_exceptions.InsufficientScopeException(" ".join([ scope for scope in token.scopes if scope not in api_scopes ]))

			"""
			If the request is authorized, check that the method is supported.
			"""
			if method == "GET":
				parameters = self._get_get_parameters(env, request)
			elif method in ["POST", "DELETE"]:
				parameters = self._get_post_parameters(env, request)
			else:
				response.status_code = 405
				response.add_header("Allow", "POST, GET")
				return response

			if api_self_only and not self._is_personal(access_token, parameters):
				"""
				Ensure that the user is trying to access their own data if the route has this safety measure.
				"""
				raise request_exceptions.UnauthorizedDataAccessException()

			if len(route) == 0:
				"""
				Ensure that the request was made using the correct method.
				"""
				raise request_exceptions.MethodNotAllowedException()

			missing_parameters = self._has_required_parameters(parameters, required_parameters)
			if len(missing_parameters):
				"""
				Ensure that the request has all the required parameters.
				"""
				raise request_exceptions.MissingArgumentException("Missing arguments: %s" % ', '.join(missing_parameters))

			"""
			Pass on all parameters - even those that are not required - to the handler function.
			"""
			return api_function(self._route_handlers[api_handler], **parameters)
		except request_exceptions.MissingArgumentException as e:
			response.status_code = 400
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
			return response
		except (request_exceptions.InvalidTokenException,
				request_exceptions.UnauthorizedDataAccessException,
				error.AccessTokenNotFound) as e:
			response.status_code = 401
			response.add_header("WWW-Authenticate", "Bearer realm=\"biobank\"")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
			return response
		except request_exceptions.InsufficientScopeException as e:
			response.status_code = 403
			response.add_header("WWW-Authenticate", ", ".join(["Bearer realm=\"biobank\"", "scope=\"%s\"" % str(e), "error=insufficient_scope"]))
			return response
		except request_exceptions.MethodNotAllowedException as e:
			response.status_code = 405
			response.add_header("Allow", ', '.join(api_method))
			return response
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })
			traceback.print_exc()
			return response

	def _get_get_parameters(self, env, request):
		"""
		Extract the parameters from a GET request.

		:param request: The original request. This includes the headers.
		:type request: :class:`oauth2.web.wsgi.Request`
		:param env: The request environment.
		:type env: dict

		:return: The parsed query string - containing the parameters - of the GET request.
		:rtype: dict
		"""

		request_body = parse.parse_qsl(env["QUERY_STRING"])
		return dict(request_body)

	def _get_post_parameters(self, env, request):
		"""
		Extract the parameters from a POST (or PUT) request.

		:param request: The original request. This includes the headers.
		:type request: :class:`oauth2.web.wsgi.Request`
		:param env: The request environment.
		:type env: dict

		:return: The parsed body - containing the parameters - of the POST request.
		:rtype: dict
		"""
		try:
			request_body_size = int(env.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0

		request_body = env['wsgi.input'].read(request_body_size)
		request_body = request_body.decode() if type(request_body) is not bytes else request_body
		if env.get('CONTENT_TYPE', "") == "application/json":
			request_body = json.loads(request_body)
			return dict(request_body)
		elif env.get("CONTENT_TYPE", "").startswith("multipart/form-data"):
			multipart_data = decoder.MultipartDecoder(request_body, env.get("CONTENT_TYPE", ""))

			request_body = {}
			name_pattern = re.compile(b"name=\"(.+)?\"")
			for part in multipart_data.parts:
				name = name_pattern.findall(part.headers.get(b"Content-Disposition"))[0].decode()
				content = part.content
				request_body[name] = content
			return request_body
		else:
			request_body = parse.parse_qsl(request_body)
			return dict(request_body)

	def _is_authorized(self, token, scopes):
		"""
		Check whether the given access token is authorized to access a protected resource.
		This validation check considers the access token's expiry and the scopes of the request.

		:param token: The supplied access token.
		:type token: :class:`oauth2.datatype.AccessToken`
		:param scopes: The scope of a route, compared with the access token's scope.
		:type scopes: str

		:return: A boolean indicating whether the given access token has enough permissions to access a protected resource.
		:rtype: bool

		:raises: :class:`server.exceptions.request_exceptions.InvalidTokenException`
		"""

		if len(scopes) > 0:
			"""
			First ensure that the token has not expired.
			"""
			if token.is_expired():
				raise request_exceptions.InvalidTokenException()

			"""
			Secondly, ensure that the access token has the required scopes.
			"""
			scope_permission = all(scope in token.scopes for scope in scopes)
			if not scope_permission:
				return False

		return True

	def _is_personal(self, access_token, parameters):
		"""
		Check whether the given access token is authorized to access a protected resource.
		The validation checks for personal data access.

		If the parameters include a username, the function checks that the access token belongs to that same user.

		:param access_token: The supplied access token.
		:type access_token: str
		:param parameters: The provided parameters.
		:type parameters: dict

		:return: A boolean indicating whether the given access token can access the protected resource.
		:rtype: bool
		"""

		token = self.access_token_store.fetch_by_token(access_token) # Fetch the token
		request_maker = token.user_id
		if ("username" in parameters and parameters.get("username") != request_maker):
			return False

		return True

	def _has_required_parameters(self, parameters, required_parameters):
		"""
		Check whether the request has all the required parameters.

		:param parameters: The full list of arguments passed on in the call.
		:type parameters: dict
		:param required_parameters: The list of required arguments.
		:type required_parameters: list

		:return: A list of missing parameters.
		:rtype: list
		"""

		"""
		Extract the missing required parameters.
		"""
		missing_parameters = [ parameter for parameter in required_parameters if parameter not in parameters ]

		return missing_parameters
