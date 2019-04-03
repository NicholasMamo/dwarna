"""
A number of custom grants supported by the authorization server.
In practice, these grants are based on existing ones and modify their behavior.
"""

from oauth2.datatype import AccessToken
from oauth2.grant import encode_scopes, json_success_response, GrantHandlerFactory, ClientCredentialsGrant, ClientCredentialsHandler, ScopeGrant

import time

class CustomClientCredentialsGrant(GrantHandlerFactory, ScopeGrant):
	"""
	The custom take on the client credentials grant sends back scopes with access tokens.
	In this way, if a scope was rejected, the client would know.
	This allows the frontend to ensure that the requested scopes were valid.

	Furthermore, the custom credentials grant allows the token expiry to be specified in the constructor.

	:ivar expires_in: The access token's lifespan, in seconds.
	:vartype expires_in: int
	"""

	"""
	The base type of the grant.
	"""
	grant_type = "client_credentials"

	def __init__(self, expires_in=30, *args, **kwargs):
		"""
		Create the client credentials grant.

		:param expires_in: The time (in seconds) for which an access token will remain valid.
		:type expires_in: int
		"""

		self.expires_in = expires_in

		super(CustomClientCredentialsGrant, self).__init__(*args, **kwargs)

	def __call__(self, request, server):
		"""
		Handles calls to give out access tokens.

		:param request: The request made to the server.
		:type request: :class:`oauth2.web.wsgi.Request`
		:param server: The server that received the request.

		:return: An access token, or none if the request is invalid.
		:rtype: dict or None
		"""

		"""
		Ensure that the request really demands a request.
		"""
		if request.path != server.token_path:
			return None

		"""
		If the grant type is supported, created a handler and get an access token.
		"""
		user_id = request.post_param("user_id")
		if request.post_param("grant_type") == self.grant_type:
			scope_handler = self._create_scope_handler()
			scope_handler.send_back = True
			return CustomClientCredentialsHandler(
				access_token_store=server.access_token_store,
				client_authenticator=server.client_authenticator,
				scope_handler=scope_handler,
				token_generator=server.token_generator,
				user_id=user_id)
		return None

class CustomClientCredentialsHandler(ClientCredentialsHandler):
	"""
	A custom implementation of the client credentials handler.

	The implementation adds functionality to store the user ID alongside the access token.
	This is the only new addition in the class.

	:ivar user_id: The owner of the access token.
		The client asks for an access token on behalf of its users.
	:vartype user_id: str
	"""

	def __init__(self, access_token_store, client_authenticator,
					scope_handler, token_generator, user_id):
		"""
		Create a new client credentials handler.
		The client credentials handler stores one added attribute - the user's ID.

		:param access_token_store: The access token store.
		:type access_token_store: :class:`oauth2.store.AccessTokenStore`
		:param client_authenticator: The client authenticator.
		:type client_authenticator: :class:`oauth2.client_authenticator.ClientAuthenticator`
		:param scope_handler: The scope handler, involved in processing scopes.
		:type scope_handler: :class:`oauth2.grant.Scope`
		:param token_generator: The class that generates access tokens.
		:type token_generator: :class:`oauth2.token_generator.TokenGenerator`
		:param user_id: The ID of the user for whom the client is generating the access token.
		:type user_id: str
		"""
		super().__init__(access_token_store, client_authenticator,
				scope_handler, token_generator)
		self.user_id = user_id

	def process(self, request, response, environ):
		"""
		Process a request for an access token.

		:param request: The request that was received.
		:type request: :class:`oauth2.web.wsgi.Request`
		:param response: The response that is being constructed.
		:type response: :class:`oauth2.web.Response`
		:param environ: The request parameters.
		:type environ: dict

		:return: The processed response.
		:rtype: :class:`oauth2.web.Response`
		"""
		body = {"token_type": "Bearer"}

		token = self.token_generator.generate()
		expires_in = self.token_generator.expires_in.get(ClientCredentialsGrant.grant_type, None)
		if expires_in is None:
			expires_at = None
		else:
			expires_at = int(time.time()) + expires_in

		access_token = AccessToken(
			client_id=self.client.identifier,
			grant_type=ClientCredentialsGrant.grant_type,
			token=token,
			expires_at=expires_at,
			scopes=self.scope_handler.scopes,
			user_id=self.user_id)
		self.access_token_store.save_token(access_token)

		body["access_token"] = token

		if expires_in is not None:
			body["expires_in"] = expires_in

		if self.scope_handler.send_back:
			body["scope"] = encode_scopes(self.scope_handler.scopes)

		json_success_response(data=body, response=response)

		return response
