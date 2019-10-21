"""
The route handler to handle email-related requests.
"""

import json
import traceback

from oauth2.web import Response

from .exceptions import general_exceptions, study_exceptions, user_exceptions
from .handler import PostgreSQLRouteHandler

class EmailHandler(PostgreSQLRouteHandler):
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
			The response contains the new email's attributes, including its ID.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			subject = self._sanitize(subject)
			body = self._sanitize(body)

			cursor = self._connector.execute(
				"""
				INSERT INTO
					emails (subject, body)
				VALUES
					('%s', '%s')
				RETURNING
					id, subject, body
				""" % (subject, body), with_cursor=True)
			email = cursor.fetchone()
			cursor.close()

			"""
			Add the recipients to the email.
			"""
			if (recipients is not None and
				type(recipients) is list):
				self._connector.bulk_execute(
					"""
					INSERT INTO
						email_recipients (email_id, recipient)
					VALUES
						%s
					""",
					[ (email['id'], recipient) for recipient in recipients ],
					"(%s, %s)"
				)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps(dict(email))
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

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

		if id is not None:
			id = int(id)

		"""
		The base SQL string returns every email.
		The placeholder allows modifications to what is returned.
		"""
		sql = """
			SELECT
				emails.* %s
			FROM
				emails %s
		"""

		"""
		Filter the emails if an ID is given.
		"""
		if id is not None:
			sql += """
				WHERE
					id = %d
			""" % id

		"""
		If the recipients are requested, return them as well.
		"""
		if recipients:
			"""
			Complete the SELECT and FROM fields.
			"""
			sql = sql % (
				", ARRAY_AGG(recipient) AS recipients",
				"""LEFT JOIN
					email_recipients
				ON
					emails.id = email_recipients.email_id"""
			)
			sql += """
				GROUP BY
					emails.id
			"""
		else:
			sql = sql % ('', '')

		"""
		Return the response.
		"""
		emails = self._connector.select(sql)

		response = Response()
		response.status_code = 200
		response.add_header("Content-Type", "application/json")
		response.body = json.dumps({ "data": emails[0] if id is not None else emails })
		return response
