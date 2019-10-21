"""
The route handler to handle email-related requests.
"""

import json
import traceback

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import RouteHandler

class EmailHandler(RouteHandler):
	"""
	The email handler class receives and handles requests that are related to emails and their recipients.
	"""

	def create_email(self, subject, body, recipients=None, recipient_group=None, *args, **kwargs):
		"""
		Insert an email into the database.

		:param subject: The email's subject.
		:type subject: str
		:param body: The email's body.
		:type body: str
		:param recipients: The email's recipients.
			If `None` is given, the recipients default to an empty list.
			Otherwise, the list is considered as a list of emails.
		:type recipients: None or list
		:param recipient_group: A recipient group that should receive the email.
			The group is represented as a string, or nothing at all.
			The conversion from the group to the actual recipients is handled by the function.
			Accepted strings:
				- 'None' - no recipient should be added
				- 'Subscribed' - only subscribed users should receive the email
				- 'All' - everyone, including unsubscribed users, should receive the email.
				  *This should be used sparingly and only when absolutely needed to respect user decisions.*
		:type recipient_group: None or str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		pass

	def remove_email(self, id, *args, **kwargs):
		"""
		Remove the email that has the given ID.

		:param id: The email's unique ID.
		:type id: str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		pass

	def get_email(self, id=None, recipients=False, *args, **kwargs):
		"""
		Get the email with the given ID.
		If no ID is given, all emails are fetched.

		Associated recipients can also be fetched.

		:param id: The email's unique id.
		:type id: str
		:param recipients: A parameter that specifies whether the email's recipients should be returned.
		:type recipients: bool

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		pass
