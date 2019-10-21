"""
Test the email management functionality in the backend.
"""

import json
import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from .environment import *

from .test import BiobankTestCase

class EmailManagementTest(BiobankTestCase):
	"""
	Test the backend's email management functionality.
	"""

	@BiobankTestCase.isolated_test
	def test_create_email(self):
		"""
		Test that creating an email works as it is supposed to.
		This test includes sanitization
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Assert that the data is correct.
		"""
		response_body = response.json()
		self.assertTrue('id' in response_body)
		self.assertGreater(response_body['id'], 0)
		self.assertEqual(subject, response_body['subject'])
		self.assertEqual(body, response_body['body'])
