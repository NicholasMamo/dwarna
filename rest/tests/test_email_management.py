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
		self.assertTrue('id' in response_body['data'])
		self.assertGreater(response_body['data']['id'], 0)
		self.assertEqual(subject, response_body['data']['subject'])
		self.assertEqual(body, response_body['data']['body'])

	@BiobankTestCase.isolated_test
	def test_create_email_with_recipients(self):
		"""
		Test that creating an email with recipients works properly.
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
		id = response_body['data']['id']

		"""
		Ensure that the recipients were saved.
		"""
		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(recipients, response_body['recipients'])

	@BiobankTestCase.isolated_test
	def test_create_email_with_recipient_group(self):
		"""
		Test that creating an email with a recipient group works properly.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."
		recipients = [ 'test@email.com' ]

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			'recipients': recipients,
			"recipient_group": 'all'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		"""
		Ensure that all recipients were saved.
		"""
		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue(recipients[0] in response_body['recipients'])
		self.assertTrue('nick@email.com' in response_body['recipients'])

	@BiobankTestCase.isolated_test
	def test_create_email_with_subscribed_recipient_group(self):
		"""
		Test that the 'subscribed' user group works correctly.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "update_subscription", "view_subscription", "create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Create an email and add the subscribed participants to it.
		The new participant should be included.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'subscribed'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue('nick@email.com' in response_body['recipients'])

		"""
		Remove the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': False
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertFalse(response_body['data']['any_email'])

		"""
		Create an email and add the subscribed participants to it.
		This time, the new participant should not be included.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'subscribed'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertFalse('nick@email.com' in response_body['recipients'])

		"""
		Re-add the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': True
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue(response_body['data']['any_email'])

		"""
		Create an email and add the subscribed participants to it.
		The new participant should be included again.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'subscribed'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue('nick@email.com' in response_body['recipients'])

	@BiobankTestCase.isolated_test
	def test_all_recipient_group_includes_unsubscribed(self):
		"""
		Test that the 'all' user group works correctly.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "update_subscription", "view_subscription", "create_email", "view_email"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Create an email and add all participants to it.
		The new participant should be included.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'all'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue('nick@email.com' in response_body['recipients'])

		"""
		Remove the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': False
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertFalse(response_body['data']['any_email'])

		"""
		Create an email and add all participants to it.
		This time, the new participant should not be included.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'all'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue('nick@email.com' in response_body['recipients'])

		"""
		Re-add the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': True
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue(response_body['data']['any_email'])

		"""
		Create an email and add all participants to it.
		The new participant should be included again.
		"""
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'all'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		response = self.send_request("GET", "email", {
			"id": id,
			"recipients": True
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertTrue('nick@email.com' in response_body['recipients'])

	@BiobankTestCase.isolated_test
	def test_create_email_with_unknown_recipient_group(self):
		"""
		Test that creating an email with an unknown recipient group raises an exception.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body,
			"recipient_group": 'unsubscribed'
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('UnknownRecipientGroupException', response_body['exception'])

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
		id = response_body['data']['id']

		"""
		Assert that the data is correct.
		"""
		response = self.send_request("GET", "email", {
			"id": id
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(id, response_body['data']['id'])
		self.assertEqual(subject, response_body['data']['subject'])
		self.assertEqual(body, response_body['data']['body'])

	@BiobankTestCase.isolated_test
	def test_get_nonexistent_email(self):
		"""
		Test getting an email that does not exist.
		"""

		token = self._get_access_token(["view_email"])["access_token"]
		response = self.send_request("GET", "email", {
			"id": 1
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('EmailDoesNotExistException', response_body['exception'])

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
		id = response_body['data']['id']

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
		id = response_body['data']['id']

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
		id = response_body['data']['id']

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
		other_id = response_body['data']['id']

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

	@BiobankTestCase.isolated_test
	def test_remove_email(self):
		"""
		Test that removing an email works as it is supposed to.
		"""

		subject = 'Ġanni żar lil Ċikku il-Ħamrun'
		body = "Ġie lura mingħand Ċikku tal-Ħamrun b'żarbun ġdid."

		token = self._get_access_token(["create_email", "view_email", "remove_email"])["access_token"]
		response = self.send_request("POST", "email", {
			"subject": subject,
			"body": body
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		id = response_body['data']['id']

		"""
		Remove the email and ensure that getting it is impossible.
		"""
		response = self.send_request("DELETE", "email", {
			"id": id
		}, token)
		self.assertEqual(response.status_code, 200)

		response = self.send_request("GET", "email", {
			"id": id
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('EmailDoesNotExistException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_remove_nonexistent_email(self):
		"""
		Test that removing an email that does not exist raises an exception.
		"""

		token = self._get_access_token(["create_email", "view_email", "remove_email"])["access_token"]
		response = self.send_request("DELETE", "email", {
			"id": 1
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('EmailDoesNotExistException', response_body['exception'])

	"""
	Filtering tests.
	"""

	@BiobankTestCase.isolated_test
	def test_email_limit(self):
		"""
		Test limiting the number of emails that are retrieved.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Create a few emails.
		"""
		for i in range(0, 10):
			subject = 'Email %s'
			body = "Body %s"

			response = self.send_request("POST", "email", {
				"subject": subject % i,
				"body": body % i
			}, token)
			self.assertEqual(response.status_code, 200)

		"""
		By default, if no number is provided, all emails should be returned.
		"""
		response = self.send_request("GET", "email", { }, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

		"""
		Try to get a negative number of emails.
		This should return all emails.
		"""
		response = self.send_request("GET", "email", {
			'number': -1
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

		"""
		Try to get zero emails.
		This should return no emails at all.
		"""
		response = self.send_request("GET", "email", {
			'number': 0
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(0, len(response_body))

		"""
		Try to get five emails.
		This should return five emails.
		"""
		response = self.send_request("GET", "email", {
			'number': 5
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(5, len(response_body))

		"""
		Try to get all emails.
		This should return all emails.
		"""
		response = self.send_request("GET", "email", {
			'number': 10
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

		"""
		Try to get more emails than exist.
		This should return all existing emails.
		"""
		response = self.send_request("GET", "email", {
			'number': 20
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

	@BiobankTestCase.isolated_test
	def test_email_pagination(self):
		"""
		Test paginating emails.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Create a few emails.
		"""
		for i in range(0, 10):
			subject = 'Email %s'
			body = "Body %s"

			response = self.send_request("POST", "email", {
				"subject": subject % i,
				"body": body % i
			}, token)
			self.assertEqual(response.status_code, 200)

		"""
		Test getting emails from a page that should be empty.
		"""
		response = self.send_request("GET", "email", {
			'number': 1,
			'page': 11
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(0, len(response_body))

		"""
		Test getting emails from a non-positive page.
		This should return the first page.
		"""
		response = self.send_request("GET", "email", {
			'number': 5,
			'page': -1
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(5, len(response_body))

		"""
		Test getting emails from the first page.
		"""
		response = self.send_request("GET", "email", {
			'number': 5,
			'page': 1
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(5, len(response_body))

		"""
		Test getting emails from the last page.
		"""
		response = self.send_request("GET", "email", {
			'number': 5,
			'page': 2
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(5, len(response_body))

		"""
		Test getting emails from the last incomplete page.
		"""
		response = self.send_request("GET", "email", {
			'number': 4,
			'page': 3
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(2, len(response_body))

	@BiobankTestCase.isolated_test
	def test_email_search(self):
		"""
		Test searching emails.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Create a few emails.
		"""
		for i in range(0, 10):
			subject = 'Email %s'
			body = "Body %s"

			response = self.send_request("POST", "email", {
				"subject": subject % i,
				"body": body % i
			}, token)
			self.assertEqual(response.status_code, 200)

		"""
		Test searching for a single email with a search string that should match the subject.
		"""
		response = self.send_request("GET", "email", {
			'search': 'Email 1'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(1, len(response_body))

		"""
		Test searching for a single email with a search string that should match the body.
		"""
		response = self.send_request("GET", "email", {
			'search': 'Body 1'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(1, len(response_body))

		"""
		Test searching for a single email with a case insensitive search string that should match the subject.
		"""
		response = self.send_request("GET", "email", {
			'search': 'email 1',
			'case_sensitive': False,
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(1, len(response_body))

		"""
		Test searching for a single email with a case insensitive search string that should match the body.
		"""
		response = self.send_request("GET", "email", {
			'search': 'body 1',
			'case_sensitive': False,
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(1, len(response_body))

		"""
		Test searching for a single email with a case sensitive search string that shouldn't match any email.
		"""
		response = self.send_request("GET", "email", {
			'search': 'email 1',
			'case_sensitive': True,
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(0, len(response_body))

		"""
		Test searching for a list of emails by looking in the subject.
		"""
		response = self.send_request("GET", "email", {
			'search': 'email',
			'case_sensitive': False,
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

		"""
		Test searching for a list of emails by looking in the body.
		"""
		response = self.send_request("GET", "email", {
			'search': 'body',
			'case_sensitive': False,
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(10, len(response_body))

		"""
		Test paginating a list of emails.
		"""
		response = self.send_request("GET", "email", {
			'search': 'email',
			'case_sensitive': False,
			'number': 4,
			'page': 3
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()['data']
		self.assertEqual(2, len(response_body))

	@BiobankTestCase.isolated_test
	def test_email_total(self):
		"""
		Test getting the total number of emails even when filtering or paginating.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		By default, there should be no emails.
		"""
		response = self.send_request("GET", "email", { }, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(0, response_body['total'])

		"""
		Create a few emails.
		"""
		ids = []
		for i in range(0, 10):
			subject = 'Email %s'
			body = "Body %s"

			response = self.send_request("POST", "email", {
				"subject": subject % i,
				"body": body % i
			}, token)
			ids.append(response.json()['data']['id'])
			self.assertEqual(response.status_code, 200)

		"""
		Now there should be 10 emails.
		"""
		response = self.send_request("GET", "email", { }, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(10, response_body['total'])

		"""
		When paginating, the correct total should be returned.
		"""
		response = self.send_request("GET", "email", {
			'number': 4,
			'page': 3
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(10, response_body['total'])

		"""
		When searching, the correct total should be returned.
		"""
		response = self.send_request("GET", "email", {
			'number': 4,
			'page': 3,
			'search': 'email',
			'case_sensitive': False
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(10, response_body['total'])

		"""
		When the search is narrower, the total should change.
		"""
		response = self.send_request("GET", "email", {
			'number': 4,
			'page': 3,
			'search': 'email 1',
			'case_sensitive': False
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(1, response_body['total'])

		response = self.send_request("GET", "email", {
			'id': ids[0]
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertEqual(1, response_body['total'])

	"""
	Email delivery tests.
	"""

	@BiobankTestCase.isolated_test
	def test_next_email_initially_empty(self):
		"""
		Test that when there are no emails, the email delivery system returns no email.
		"""

		token = self._get_access_token(["view_email"])["access_token"]

		"""
		Initially, there should be no emails to send.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

	@BiobankTestCase.isolated_test
	def test_next_email_without_recipients(self):
		"""
		Test that if an email has no recipients, it is not returned.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Initially, there should be no emails to send.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

		"""
		Create an email.
		"""
		response = self.send_request("POST", "email", {
			"subject": "subject",
			"body": "body"
		}, token)
		id = response.json()['data']['id']
		self.assertEqual(response.status_code, 200)

		"""
		Since the email has no recipients, it should not be returned for delivery.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

	@BiobankTestCase.isolated_test
	def test_next_email(self):
		"""
		Test that if an email has recipients who have not received the email yet, it is returned.
		"""

		token = self._get_access_token(["create_email", "view_email"])["access_token"]

		"""
		Initially, there should be no emails to send.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

		"""
		Create an email.
		"""
		response = self.send_request("POST", "email", {
			"subject": "subject",
			"body": "body",
			'recipients': [ 'nicholas.mamo@um.edu.mt' ],
		}, token)
		id = response.json()['data']['id']
		self.assertEqual(response.status_code, 200)

		"""
		This email should be returned as has recipients.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()['data']
		self.assertEqual(response.status_code, 200)
		self.assertEqual(id, response_body['email']['id'])

	@BiobankTestCase.isolated_test
	def test_send_email(self):
		"""
		Test that if an email has recipients who have not received the email yet, it is returned.
		"""

		token = self._get_access_token(["create_email", "view_email", "deliver_email"])["access_token"]

		"""
		Initially, there should be no emails to send.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

		"""
		Create an email.
		"""
		response = self.send_request("POST", "email", {
			"subject": "subject",
			"body": "body",
			'recipients': [ 'nicholas.mamo@um.edu.mt' ],
		}, token)
		id = response.json()['data']['id']
		self.assertEqual(response.status_code, 200)

		"""
		This email should now have been sent.
		"""
		response = self.send_request("POST", "delivery", {
			"simulated": True
		}, token)
		response_body = response.json()['data']
		self.assertEqual(response.status_code, 200)
		self.assertEqual(id, response_body['email']['id'])

		"""
		Now, there should be no more emails to send.
		"""
		response = self.send_request("GET", "delivery", { }, token)
		response_body = response.json()
		self.assertEqual(response.status_code, 200)
		self.assertEqual({}, response_body['data'])

	"""
	Email subscription tests.
	"""

	@BiobankTestCase.isolated_test
	def test_get_subscription(self):
		"""
		Test that getting a participant's subscription works.
		"""

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "view_subscription"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue('any_email' in response_body['data'])
		self.assertTrue(response_body['data']['any_email'])

	@BiobankTestCase.isolated_test
	def test_get_subscription_of_nonexistent_participant(self):
		"""
		Test that getting the subscription does not work if the participant does not exist.
		"""

		"""
		Try to get a participant's subscription.
		"""
		token = self._get_access_token(["view_subscription"])["access_token"]
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('ParticipantDoesNotExistException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_get_subscription_without_participant(self):
		"""
		Test that getting the subscription does not work if the participant is not provided.
		"""

		"""
		Try to get a participant's subscription.
		"""
		token = self._get_access_token(["view_subscription"])["access_token"]
		response = self.send_request("GET", "subscription", { }, token)
		self.assertEqual(response.status_code, 400)
		response_body = response.json()
		self.assertEqual('MissingArgumentException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_get_unknown_subscription(self):
		"""
		Test that getting a participant's subscription does not work if the subscription is unknown.
		"""

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "view_subscription"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Try to get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'no_email'
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('UnknownSubscriptionTypeException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_get_all_subscriptions(self):
		"""
		Test that getting all of a participant's subscription works.
		"""

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "view_subscription"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue('any_email' in response_body['data'])

	@BiobankTestCase.isolated_test
	def test_update_subscription(self):
		"""
		Test that updating a participant's subscription works.
		"""

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "update_subscription", "view_subscription"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue(response_body['data']['any_email'])

		"""
		Remove the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': False
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertFalse(response_body['data']['any_email'])

		"""
		Re-add the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': True
		}, token)
		self.assertEqual(response.status_code, 200)

		"""
		Get the participant's subscription.
		"""
		response = self.send_request("GET", "subscription", {
			'username': 'nick',
			'subscription': 'any_email'
		}, token)
		self.assertEqual(response.status_code, 200)
		response_body = response.json()
		self.assertTrue(response_body['data']['any_email'])

	@BiobankTestCase.isolated_test
	def test_update_subscription_of_nonexistent_participant(self):
		"""
		Test that updating the subscription does not work if the participant does not exist.
		"""

		"""
		Try to update a participant's subscription.
		"""
		token = self._get_access_token(["update_subscription"])["access_token"]
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
			'subscribed': True
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('ParticipantDoesNotExistException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_update_subscription_without_participant(self):
		"""
		Test that updating the subscription does not work if the participant is not provided.
		"""

		"""
		Try to update a participant's subscription.
		"""
		token = self._get_access_token(["update_subscription"])["access_token"]
		response = self.send_request("POST", "subscription", {
			'subscription': 'any_email',
			'subscribed': True,
		}, token)
		self.assertEqual(response.status_code, 400)
		response_body = response.json()
		self.assertEqual('MissingArgumentException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_update_unknown_subscription(self):
		"""
		Test that updating a participant's subscription does not work if the subscription is unknown.
		"""

		"""
		Create a participant.
		"""
		token = self._get_access_token(["create_participant", "view_subscription", "update_subscription"])["access_token"]
		response = self.send_request("POST", "participant", { "username": "nick", "email": 'nick@email.com' }, token)
		self.assertEqual(response.status_code, 200)

		"""
		Try to update the participant's subscription.
		"""
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'no_email',
			'subscribed': True,
		}, token)
		self.assertEqual(response.status_code, 500)
		response_body = response.json()
		self.assertEqual('UnknownSubscriptionTypeException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_update_subscription_without_subscription(self):
		"""
		Test that updating the subscription does not work if the subscription type is not provided.
		"""

		"""
		Try to update a participant's subscription.
		"""
		token = self._get_access_token(["update_subscription"])["access_token"]
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscribed': True,
		}, token)
		self.assertEqual(response.status_code, 400)
		response_body = response.json()
		self.assertEqual('MissingArgumentException', response_body['exception'])

	@BiobankTestCase.isolated_test
	def test_update_subscription_without_subscription_change(self):
		"""
		Test that updating the subscription does not work if the subscription value is not provided.
		"""

		"""
		Try to update a participant's subscription.
		"""
		token = self._get_access_token(["update_subscription"])["access_token"]
		response = self.send_request("POST", "subscription", {
			'username': 'nick',
			'subscription': 'any_email',
		}, token)
		self.assertEqual(response.status_code, 400)
		response_body = response.json()
		self.assertEqual('MissingArgumentException', response_body['exception'])
