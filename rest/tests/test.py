"""
Creates the setup for the tests.
"""

import functools
import json
import os
import requests
import signal
import sys
import time
import unittest

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from biobank.handlers.exceptions import general_exceptions, user_exceptions

from .environment import *

def retry(times=10):
	"""
	A decorator function that keeps trying to get a result until it times out.
	The function is useful in cases where results are not available immediately.
	This case arises when the blockchain needs to be mined before getting a result.

	:param times: The number of times that the function should be retried.
		If the desired status is never received, the function returns the last output.
	:type times: int

	:return: The wrapped function.
	:rtype: func
	"""

	def attempt(function, *args, **kwargs):
		"""
		The function that takes care of attempts.

		:param function: The function to retry.
		:type function: func
		"""

		@functools.wraps(function)

		def wrapper_retry(status_code=200, value=None, *args, **kwargs):
			"""
			Retry the function a number of times.

			:param function: The function to retry.
			:type function: func
			:param status_code: The expected status that the function should return.
				The status corresponds to an HTTP status code.
			:type status_code: int
			:param value: The desired return value.
			:type: value

			:return: The response.
			:rtype: :class:`requests.models.Response`
			"""

			for i in range(0, times):
				response = function(*args, **kwargs)
				if (response.status_code == status_code and
					(value is None or value == response.json()["data"])):
					break
				time.sleep(1)

			return response

		return wrapper_retry

	return attempt

class BiobankTestCase(unittest.TestCase):
	"""
	Test the schema.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Connect with the database, create the schema and start the server.
		"""

		create_testing_environment()
		main.main(TEST_DATABASE, TEST_OAUTH_DATABASE, PORT)
		time.sleep(1) # wait so as not to overload the server with requests

	@classmethod
	def tearDownClass(self):
		"""
		At the end of the tests, stop the server.
		"""

		if main.pid is not None:
			os.kill(main.pid, signal.SIGINT)

	def _get_access_token(self, scopes, user_id="admin"):
		"""
		Fetch the access token.

		:param scopes: The list of scopes that are required.
		:type scopes: list
		:param user_id: The user on whose behalf an access token will be fetched.
		:type user_id: str

		:return: The access token to be used throughout the tests.
		:rtype: dict
		"""

		data = {
			"grant_type": "client_credentials",
			"client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRET,
			"scope": ' '.join(scopes),
			"user_id": user_id
		}

		response = requests.post('http://localhost:%d/token' % PORT, data=data)
		return response.json()

	def send_volatile_request(self, method, endpoint, data, access_token, status_code=200, value=None):
		"""
		Send a volatile request to the backend.
		A volatile request is one whose return value is expected to change over time.
		The request is retried until the desired value is returned, or until some time passes.

		:param method: The method to use when sending the request - usually POST or GET.
		:type method: str
		:param endpoint: The endpoint to which to make the request.
		:type endpoint: str
		:param data: The data to send along with the request.
		:type data: dict
		:param access_token: The access token to use to retrieve protected resources.
		:type access_token: str
		:param status_code: The expected status that the function should return.
			The status corresponds to an HTTP status code.
			By default, the function expects the request to succeed.
		:type status_code: int
		:param value: The desired return value.
		:type: value

		:return: The response.
		:rtype: :class:`requests.models.Response`
		"""

		volatile_request = retry(times=60)
		return volatile_request(self.send_request)(status_code, value, method, endpoint, data, access_token)

	def send_request(self, method, endpoint, data, access_token):
		"""
		Send a request to the backend.

		:param method: The method to use when sending the request - usually POST or GET.
		:type method: str
		:param endpoint: The endpoint to which to make the request.
		:type endpoint: str
		:param data: The data to send along with the request.
		:type data: dict
		:param access_token: The access token to use to retrieve protected resources.
		:type access_token: str

		:return: The response.
		:rtype: :class:`requests.models.Response`
		"""

		method_handler = {
			"POST": requests.post,
			"GET": requests.get,
			"DELETE": requests.delete,
		}.get(method.upper())

		headers = { "Authorization": access_token }

		if method.upper() == "GET":
			return method_handler('http://localhost:%d/%s' % (PORT, endpoint), params=data, headers=headers)
		else:
			return method_handler('http://localhost:%d/%s' % (PORT, endpoint), json=data, headers=headers)
