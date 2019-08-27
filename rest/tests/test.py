"""
Creates the setup for the tests.
"""

import functools
import json
import os
import requests
import signal
import subprocess
import sys
import time
import unittest
import uuid
import zipfile

from functools import wraps

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from biobank.handlers.exceptions import general_exceptions, user_exceptions

from tests.environment import *

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
		main.main(TEST_DATABASE, TEST_OAUTH_DATABASE, PORT, single_card=False)
		time.sleep(1) # wait so as not to overload the server with requests

	@classmethod
	def tearDownClass(self):
		"""
		At the end of the tests, stop the server.
		"""

		if main.pid is not None:
			os.kill(main.pid, signal.SIGINT)

	def isolated_test(test):
		"""
		Perform the test in isolation.
		In essence, this means that the data is cleared from the database.

		:param test: The test to perform.
		:type test: function
		"""

		@wraps(test)

		def wrapper(*args):
			"""
			The wrapper removes all data from the database.
			"""

			clear()
			test(*args)

		return wrapper

	"""
	Make the isolated test a static method.
	NOTE: This should be done after the methods in this class that use this decorator have already been defined.
	"""
	isolated_test = staticmethod(isolated_test)

	def _generate_study_name(self, prefix="t"):
		"""
		Generate a new name for a study with the goal of avoiding overlapping names in the blockchain.

		The name is formed by generating a UUID and prepending it with a prefix.

		:param prefix: A string to prepend to every test name.
		:type prefix: str
		:return: A random study ID.
		:rtype: str
		"""

		return f"{prefix}-{str(uuid.uuid4())}"

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
			"PUT": requests.put,
		}.get(method.upper())

		headers = { "Authorization": access_token }

		if method.upper() == "GET":
			return method_handler('http://localhost:%d/%s' % (PORT, endpoint), params=data, headers=headers)
		else:
			return method_handler('http://localhost:%d/%s' % (PORT, endpoint), json=data, headers=headers)

class rest_context(BiobankTestCase):
	"""
	The REST context class creates a new Hyperledger Composer REST API to service requests.

	The class takes care of starting and stopping the Hyperledger Composer REST API.
	This REST API is used instead of starting a multi-user Hyperledger Composer REST API.
	This is not possible because the user cannot authenticate themselves.
	Instead, a REST API server is created just for them.

	:ivar _participant: The participant on whose behalf the REST API will be started.
	:vartype _participant: str or int
	:ivar _port: The port where the REST API will be started.
	:vartype _port: int
	:ivar _study_id: The study ID for which the card will be fetched.
					 This card is used to start the Hyperledger Composer REST API.
	:vartype _study_id: str
	:ivar _subprocess: The subprocess that is running the Hyperledger Composer REST API.
	:vartype _subprocess: :class:`subprocess.Popen`
	"""

	def __init__(self, participant, port, study_id):
		"""
		Create the REST API context.
		This context represents the participant for whom to serve the REST API.

		:param participant: The participant on whose behalf the REST API will be started.
		:type participant: str or int
		:param port: The port where the REST API will be started.
		:type port: int
		:param study_id: The study ID for which the card will be fetched.
						 This card is used to start the Hyperledger Composer REST API.
		:type study_id: str
		"""

		self._participant = participant
		self._port = port
		self._study_id = study_id

	def __enter__(self):
		"""
		When the context is opened, run the REST API.
		"""

		return self.start_rest(self._participant, self._port, self._study_id)

	def __exit__(self, type, value, traceback):
		"""
		When the context is closed, stop the REST API.
		"""

		self.stop_rest(self._port)

	def start_rest(self, participant, port, study_id):
		"""
		Start the REST API using the given card name.

		:param participant: The participant for whom the REST API will start.
		:type: participant: str
		:param port: The port where to open the REST API.
		:type port: int
		:param study_id: The ID of the study which the REST API should handle.
		:type study_id: int

		:return: The user's address on the blockchain.
		:rtype: str
		"""

		"""
		Get an access token from the biobank REST API to change their card.
		Then, get the card for the study and save it to disk.
		"""
		token = self._get_access_token(["change_card"], participant)["access_token"]
		response = self.send_request("GET", "get_card", {
			"username": f"p{participant}",
			"study_id": study_id,
			"temp": True
		}, token)
		card_name = f"p{participant}.card"
		self.save_card(response.content, card_name)

		"""
		Create a new Hyperledger Composer REST API that is served using the participant's card.
		"""
		script_dir = os.path.dirname(os.path.realpath(__file__))
		proc = subprocess.Popen([
				"bash", os.path.join(script_dir, "start_rest.sh"),
				card_name, str(port)
			], close_fds=True)
		self._subprocess = proc

		"""
		Read the card and unzip it.
		From the `metadata.json` file, extract  the participant's address.
		"""
		address = ''
		with zipfile.ZipFile(os.path.join(script_dir, 'cards', card_name), 'r') as zip:
			with zip.open('metadata.json') as metadata:
				data = metadata.readline()
				address = json.loads(data)['userName']

		"""
		Wait for the REST API to start.
		"""
		time.sleep(10)
		return address

	def stop_rest(self, port):
		"""
		Stop the REST API being served on the given port.

		:param port: The port where to the REST API is being served.
		:type port: int
		"""

		"""
		Send an interrupt signal to the Hyperledger Composer REST API.
		"""
		cmd = f"kill -2 $( lsof -i:{port} -t )"
		proc = subprocess.check_output(["bash", "-i", "-c", cmd])

		"""
		Kill the bash script that started the Hyperledger Composer REST API.
		"""
		self._subprocess.kill()
		out, _ = self._subprocess.communicate()
		self._subprocess.wait()

	def save_card(self, card, card_name, dir="cards"):
		"""
		Save the provided card to a file.

		:param card: The card data to save.
		:type card: bytes
		:param card_name: The target filename.
		:type card_name: str
		:param dir: The target directory, relative to this script.
		:type dir: str
		"""

		script_dir = os.path.dirname(os.path.realpath(__file__))
		with open(os.path.join(script_dir, dir, card_name), "wb") as f:
			f.write(card)
