"""
The server that handles all requests to the backend
"""

"""
The database used by default
"""
DEFAULT_DATABASE = "biobank"

from multiprocessing import Process

from oauth2 import Provider
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import Response
from oauth2.web.wsgi import Application, Request

from urllib import parse
from wsgiref.simple_server import make_server, WSGIRequestHandler

import json
import signal

import os
from os.path import expanduser

import psycopg2
from psycopg2 import IntegrityError

class OAuthRequestHandler(WSGIRequestHandler):
	"""
	Request handler that enables formatting of the log messages on the console.
	This handler is used by the python-oauth2 application.
	"""
	def address_string(self):
		return "python-oauth2"

class TestProvider(Provider):

	def add_grant(self, grant):
		super(TestProvider, self).add_grant(grant)
		print(self.access_token_store.access_tokens)

	def dispatch(self, request, environ):
		response = super(TestProvider, self).dispatch(request, environ)
		return response

	def is_authorized(self, access_token, scope):
		return True
		token = self.access_token_store.fetch_by_token(access_token)
		if token.is_expired():
			print("expired token")
			return False
		if scope not in token.scopes:
			print(scope, "not in", token.scopes)
			return False
		return True

class OAuthApplication(Application):

	def __init__(self, provider, authorize_uri="/authorize", env_vars=None,
				 request_class=Request, token_uri="/token"):
		self._routes = {
			"/authenticated": self.is_authenticated,
			"/create_participant": self.create_participant,
		}
		super(OAuthApplication, self).__init__(provider, authorize_uri, env_vars, request_class, token_uri)
		self._pcon = PostgreSQLConnection()

	def _serve_application(self, env):
		handler = self._routes.get(env["PATH_INFO"])
		return handler(env)

	def __call__(self, env, start_response):
		environ = {}

		if (env["PATH_INFO"] != self.authorize_uri
			and env["PATH_INFO"] != self.token_uri
			and env["PATH_INFO"] not in self._routes):
			start_response("404 Not Found",
						   [('Content-type', 'text/html')])
			return [b"Not Found"]

		request = self.request_class(env)

		if isinstance(self.env_vars, list):
			for varname in self.env_vars:
				if varname in env:
					environ[varname] = env[varname]

		if env["PATH_INFO"] in self._routes:
			response = self._serve_application(env)
		else:
			response = self.provider.dispatch(request, environ)

		start_response(self.HTTP_CODES[response.status_code],
					   list(response.headers.items()))

		return [response.body.encode('utf-8')]

	def create_participant(self, env):
		response = Response()
		response.add_header("Content-Type", "application/json")
		if self.provider.is_authorized(env.get("HTTP_AUTHORIZATION"), "authentication"):
			try:
				request_body_size = int(env.get('CONTENT_LENGTH', 0))
			except (ValueError):
				request_body_size = 0

			print(env.get("CONTENT_TYPE", "No content type"))
			request_body = env['wsgi.input'].read(request_body_size).decode()
			request_body = dict(parse.parse_qsl(request_body))
			self._pcon.insert_participant(request_body["username"])

			response.status_code = 200
			response.body = json.dumps({
				"status": "success",
			})
			return response
		else:
			response.status_code = 403
			response.body = json.dumps({
				"status": "denied",
			})
			return response

	def is_authenticated(self, env):
		response = Response()
		response.add_header("Content-Type", "application/json")
		if self.provider.is_authorized(env.get("HTTP_AUTHORIZATION"), "authentication"):
			response.status_code = 200
			response.body = json.dumps({
				"status": "success",
			})
			return response
		else:
			response.status_code = 403
			response.body = json.dumps({
				"status": "denied",
			})
			return response

def run_auth_server():
	try:
		client_store = ClientStore()
		client_store.add_client(client_id="abc", client_secret="xyz",
								redirect_uris=["http://localhost:8081/callback"])

		token_store = TokenStore()

		provider = TestProvider(
			access_token_store=token_store,
			auth_code_store=token_store,
			client_store=client_store,
			token_generator=Uuid4())

		app = OAuthApplication(provider=provider)

		httpd = make_server('', 8080, app, handler_class=OAuthRequestHandler)

		print("Starting OAuth2 server on http://localhost:8080/...")
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()

def main():
	auth_server = Process(target=run_auth_server)
	auth_server.start()

	def sigint_handler(signal, frame):
		print("Terminating servers...")
		auth_server.terminate()
		auth_server.join()

	signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
	main()
