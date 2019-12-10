#!/usr/bin/env python3

"""
A script to deliver emails that have not been sent yet.
"""

import argparse
import requests

from config import oauth

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:
		- -p --port		The port on which to serve the REST API, defaults to 7225.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Serve the REST API which controls the dynamic consent functionality.")
	parser.add_argument("-p", "--port", nargs="+", type=str, default=7225, help="<Optional> The port on which to serve the REST API, defaults to 7225.", required=False)
	args = parser.parse_args()
	return args

def main(port):
	"""
	Deliver the next email.

	:param port: The port on which the REST API is listening.
	:type port: int
	"""

	access_token = _get_access_token(port, [ 'deliver_email' ], 'delivery_service')['access_token']
	email = _deliver_email(port, access_token)

def _get_access_token(port, scopes, user_id="admin"):
	"""
	Fetch the access token.

	:param port: The port on which the REST API is listening.
	:type port: int
	:param scopes: The list of scopes that are required.
	:type scopes: list
	:param user_id: The user on whose behalf an access token will be fetched.
	:type user_id: str

	:return: The returned access token.
	:rtype: dict
	"""

	data = {
		"grant_type": "client_credentials",
		"client_id": oauth.client_id,
		"client_secret": oauth.client_secret,
		"scope": ' '.join(scopes),
		"user_id": user_id
	}

	response = requests.post(f"http://localhost:{port}/token", data=data)
	return response.json()

def _deliver_email(port, access_token):
	"""
	Deliver the next email.

	:param port: The port on which the REST API is listening.
	:type port: int
	:param access_token: The access token to send with the request.
	:type access_token: str

	:return: The delivered email.
	:rtype: dict
	"""

	headers = { "Authorization": access_token }
	data = { 'max_recipients': 20 }

	response = requests.post(f"http://localhost:{port}/delivery", json=data, headers=headers)
	return response.json()

if __name__ == "__main__":
	args = setup_args()
	port = args.port
	main(port)
