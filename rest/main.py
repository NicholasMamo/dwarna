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

from threads.thread_manager import ThreadManager

from biobank.handlers.blockchain.api.hyperledger import HyperledgerAPI

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

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Serve the REST API which controls the dynamic consent functionality.")
	parser.add_argument("-p", "--port", nargs="+", type=str, help="<Optional> The port on which to serve the REST API, defaults to 7225.", required=False)
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
		client_store.add_client(client_id="abc", client_secret="xyz")

		"""
		Create a token store.
		"""
		token_store = PostgresqlAccessTokenStore(oauth_connection)

		"""
		Create the authentication and resource servers.
		The resource server is given the access token store to validate requests.
		The routes and their handler are also passed on as arguments.
		"""
		blockchain_handler = HyperledgerAPI(
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
		route_handlers[HyperledgerAPI] = blockchain_handler

		resource_provider = ResourceServer(
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

		port = int(port)
		httpd = make_server('', port, app, handler_class=OAuthRequestHandler)

		print("Starting OAuth2 server on http://localhost:%d/..." % (port))
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()

def main(database, oauth_database, listen_port=None, token_expiry=oauth.token_expiry):
	"""
	Establish a connection with PostgreSQL and start the server.

	:param database: The name of the database to connect to.
	:type database: str
	:param oauth_database: The name of the database to connect to for OAuth storage.
	:type oauth_database: str
	:param listen_port: The port on which to serve the REST API.
	:type listen_port: int
	:param token_expiry: The time taken for an access token delivered by the authorization server to expire.
		This should only be provided in testing environments.
		Otherwise, the configuration should be updated.
	:type token_expiry: int
	"""

	args = setup_args()

	"""
	Get the listen port.
	If it was not provided as an argument, it is sought as a command-line argument.
	"""
	if listen_port is None:
		listen_port = args.port[0] if args.port else 7225

	if args.single_card:
		blockchain.multi_card = False

	"""
	Get the connection details from the .pgpass file.
	Then, create connections to the server's database and to the OAuth 2.0 database.
	"""
	home = expanduser("~")
	with open(os.path.join(home, ".pgpass"), "r") as f:
		host, port, _, username, password = f.readline().strip().split(":")
	connection = routes.handler_connector(database=database, host=host, username=username, password=password)
	oauth_connection = routes.handler_connector(database=oauth_database, host=host, username=username, password=password, cursor_factory=cursor)

	global pid
	pid = os.getpid()

	"""
	Start the OAuth 2.0 server.
	"""

	auth_server = Process(target=start_auth_server, args=(listen_port, token_expiry, connection, oauth_connection))
	auth_server.start()

	def sigint_handler(signal, frame):
		print("Terminating servers...")
		auth_server.terminate()
		auth_server.join()
		connection.close()

	signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
	main(db.database, db.oauth_database, 7225)
	print("To test getting OAuth2 tokens:")
	print("curl --ipv4 -v -X POST \\")
	print("\t-d 'grant_type=client_credentials&client_id=abc&client_secret=xyz' \\")
	print("\t-d 'scope=create_participant create_researcher' \\")
	print("\thttp://localhost:8080/token")
	print()
