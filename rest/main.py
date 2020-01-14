#!/usr/bin/env python3

"""
The server that handles all requests to the backend.
"""

from multiprocessing import Process

from oauth2.grant import RefreshToken
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web.wsgi import Application, Request
from threading import Thread
from wsgiref.simple_server import make_server

import argparse
import signal
import sys

import os
from os.path import expanduser

import psycopg2
from psycopg2.extensions import cursor

"""
Biobank-specific classes.
"""

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__))))

from threads.thread_manager import ThreadManager

from biobank.handlers.blockchain.api.hyperledger import hyperledger

from coauth.grants.grants import CustomClientCredentialsGrant
from coauth.token_store.postgresql_token_store import PostgresqlAccessTokenStore, PostgresqlAuthCodeStore, PostgresqlClientStore
from coauth.oauth_request_handler import OAuthRequestHandler

from server.application import OAuthApplication
from server.resource_server import ResourceServer
from server.authorization_server import AuthorizationServer

from config import blockchain, db, oauth, routes

pid = None
"""
The PID of the REST server. Used in case it needs to be killed programmatically.
"""

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:
		- -p --port		The port on which to serve the REST API, defaults to 7225.
		- --single-card	Run the server in single-card mode.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Serve the REST API which controls the dynamic consent functionality.")
	parser.add_argument("-p", "--port", nargs="+", type=int, default=7225, help="<Optional> The port on which to serve the REST API, defaults to 7225.", required=False)
	parser.add_argument("--single-card", help="Run the server in single-card mode.", action="store_true")
	args = parser.parse_args()
	return args

def start_auth_server(port, token_expiry, connection, oauth_connection):
	"""
	Start the authorization server on the given port.

	:param port: The port on which the server listens.
	:type port: int
	:param token_expiry: The time taken for an access token delivered by the authorization server to expire.
	:type token_expiry: int
	:param connection: The database connection to use.
	:type connection: :class:`connection.connection.Connection`
	:param oauth_connection: The database connection to use for OAuth.
	:type oauth_connection: :class:`connection.connection.Connection`
	"""

	try:
		client_store = PostgresqlClientStore(oauth_connection)
		client_store.add_client(client_id=oauth.client_id, client_secret=oauth.client_secret)

		"""
		Create a token store.
		"""
		token_store = PostgresqlAccessTokenStore(oauth_connection)

		"""
		Create the authentication and resource servers.
		The resource server is given the access token store to validate requests.
		The routes and their handler are also passed on as arguments.
		"""
		blockchain_handler = hyperledger.HyperledgerAPI(
			blockchain.host,
			blockchain.admin_port,
			blockchain.multiuser_port,
			connection
		)

		"""
		Create a thread manager since some functionality uses threading.
		This thread manager routinely checks for dead threads.
		"""
		thread_list = []
		thread_manager = ThreadManager(thread_list)
		thread = Thread(target=thread_manager.run)
		thread.start()

		"""
		The route handlers are a set of classes that handle different requests.
		"""
		route_handlers = { handler_class: handler_class(connection, blockchain_handler, thread_list)
							for handler_class in routes.handler_classes }
		route_handlers[hyperledger.HyperledgerAPI] = blockchain_handler

		resource_provider = ResourceServer(
			connection=connection,
			access_token_store=token_store,
			auth_code_store=PostgresqlAuthCodeStore(oauth_connection),
			client_store=PostgresqlClientStore(oauth_connection),
			token_generator=Uuid4(),
			routes=routes.routes,
			route_handlers=route_handlers)

		"""
		The authorization server gives out access tokens.
		"""
		authorization_server = AuthorizationServer(
			access_token_store=token_store,
			auth_code_store=token_store,
			client_store=client_store,
			token_generator=Uuid4(),
		)

		client_credentials_grant = CustomClientCredentialsGrant(
			expires_in=token_expiry,
			scopes=oauth.scopes,
			default_scope=oauth.default_scope
		)
		authorization_server.add_grant(client_credentials_grant)

		app = OAuthApplication(resource_provider=resource_provider, authorization_server=authorization_server)

		if port is not None:
			port = int(port)
			httpd = make_server('', port, app, handler_class=OAuthRequestHandler)

			print("Starting OAuth2 server on http://localhost:%d/..." % (port))
			httpd.serve_forever()
		return app
	except KeyboardInterrupt:
		httpd.server_close()

def main(database, oauth_database, listen_port=None, single_card=None, token_expiry=oauth.token_expiry, dev=True):
	"""
	Establish a connection with PostgreSQL and start the server.

	:param database: The name of the database to connect to.
	:type database: str
	:param oauth_database: The name of the database to connect to for OAuth storage.
	:type oauth_database: str
	:param listen_port: The port on which to serve the REST API.
	:type listen_port: int
	:param single_card: A boolean indicating whether the server should run in single-card mode.
	:type single_card: bool
	:param token_expiry: The time taken for an access token delivered by the authorization server to expire.
		This should only be provided in testing environments.
		Otherwise, the configuration should be updated.
	:type token_expiry: int
	:param dev: A boolean indicating whether the server is in development or not.
	:type dev: bool

	:return: The WSGI server application or None if it is not in development
	:rtype: server.application.OAuthApplication or None
	"""

	"""
	Get the card operation mode.
	If it was not provided as an argument, it is sought as a command-line argument.
	"""
	if single_card is None:
		args = setup_args()
		blockchain.multi_card = not args.single_card
	else:
		blockchain.multi_card = not single_card

	"""
	Get the connection details from the .pgpass file.
	Then, create connections to the server's database and to the OAuth 2.0 database.
	"""
	connection = routes.handler_connector.connect(database)
	oauth_connection = routes.handler_connector.connect(oauth_database, cursor_factory=cursor)

	global pid
	pid = os.getpid()

	"""
	Start the OAuth 2.0 server.
	"""

	if dev:
		auth_server = Process(target=start_auth_server, args=(listen_port, token_expiry, connection, oauth_connection))
		auth_server.start()

		def sigint_handler(signal, frame):
			print("Terminating servers...")
			auth_server.terminate()
			auth_server.join()
			connection.close()

		signal.signal(signal.SIGINT, sigint_handler)
	else:
		app = start_auth_server(listen_port, token_expiry, connection, oauth_connection)
		return app

if __name__ == "__main__":
	args = setup_args()
	port = args.port[0] if type(args.port) is not int else args.port
	app = main(db.database, db.oauth_database, port, dev=True)

	print("To test the REST API:")
	print("curl --ipv4 -v POST \\")
	print(f"\t-d 'grant_type=client_credentials&client_id={oauth.client_id}&client_secret={oauth.client_secret}' \\")
	print("\t-d 'scope=create_participant create_researcher' \\")
	print(f"\thttp://localhost:{port}/token")
	print()
	print("curl -I -X GET \\")
	print("\t-h 'authorization: ACCESS_TOKEN' \\")
	print(f"\thttp://localhost:{port}/ping")
	print()
elif __name__.startswith('_mod_wsgi_'):
	app = main(db.database, db.oauth_database, None, dev=False)

def application(env, start_response):
	global app
	return app.__call__(env, start_response)
