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
		This test includes sanitization.
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

	@BiobankTestCase.isolated_test
	def test_create_email_with_participants(self):
		"""
		Test that creating an email with participants.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."
		recipients = [ 'test@email.com' ]

		token = self._get_access_token(["create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipients": recipients
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['id']

		"""
		Ensure that the participants were saved.
		"""
		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(recipients, response_body['recipients'])

	@BiobankTestCase.isolated_test
	def test_create_email_without_subject(self):
		"""
		Test that creating an email needs a subject to be provided.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"body": body
		}, token)
		self.assertEqual(response.status_code, 400)

	@BiobankTestCase.isolated_test
	def test_create_email_without_body(self):
		"""
		Test that creating an email needs a body to be provided.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject
		}, token)
		self.assertEqual(response.status_code, 400)

	@BiobankTestCase.isolated_test
	def test_get_email(self):
		"""
		Test getting an email.
		The test is simple and looks only to retrieve the basic information, not the recipients.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {
			"id": id
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(id, response_body['id'])
		self.assertEqual(subject, response_body['subject'])
		self.assertEqual(body, response_body['body'])

	@BiobankTestCase.isolated_test
	def test_get_all_emails(self):
		"""
		Test getting all emails.
		The test is simple and looks only to retrieve the basic information, not the recipients.
		"""

		subject = 'Email %s'
		body = "Body %s"
		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Assert that initially there are no emails.
		"""
		response = self.send_request("GET", "email", {}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(0, len(response_body))

		"""
		Create the first email.
		"""

		response = self.send_request("POST", "email", {
			"subject": subject % 1,
			"body": body % 1
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(1, len(response_body))
		self.assertEqual(id, response_body[0]['id'])
		self.assertEqual(subject % 1, response_body[0]['subject'])
		self.assertEqual(body % 1, response_body[0]['body'])

		"""
		Create the second email.
		"""

		response = self.send_request("POST", "email", {
			"subject": subject % 2,
			"body": body % 2
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(2, len(response_body))
		self.assertEqual(subject % 2, response_body[1]['subject'])
		self.assertEqual(body % 2, response_body[1]['body'])

	@BiobankTestCase.isolated_test
	def test_get_email_recipients(self):
		"""
		Test getting an email and its recipients.
		The test is simple and looks only to retrieve the basic information, not the recipients.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."
		recipients = [ 'test1@email.com', 'test2@email.com' ]

		token = self._get_access_token(["create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipients": recipients
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(recipients, response_body['recipients'])

		"""
		Add another email and ensure that the recipients are delivered with the right email.
		"""

		other_recipients = [ 'test3@email.com', 'test4@email.com' ]

		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipients": other_recipients
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		other_id = response_body['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {
			"id": other_id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(other_recipients, response_body['recipients'])

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(recipients, response_body['recipients'])
