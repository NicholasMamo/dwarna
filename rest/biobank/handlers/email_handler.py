"""
The route handler to handle email-related requests.
"""

import json
import os
import smtplib
import ssl
import sys
import traceback

from email.mime.text import MIMEText

path = sys.path[0]
path = os.path.join(path, "../../")
if path not in sys.path:
	sys.path.insert(1, path)

from oauth2.web import Response

from .exceptions import email_exceptions, user_exceptions
from .handler import PostgreSQLRouteHandler

from config import email as smtp
from partials import email_partials

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

								**This should be used sparingly and only when absolutely needed to respect user decisions.**

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

			if recipient_group is None or recipient_group.lower() == "none":
				recipient_list = []
			elif recipient_group.lower() == "subscribed":
				rows = self._connector.select("""
					SELECT
						participants.email
					FROM
						participants JOIN participant_subscriptions
							ON participants.user_id = participant_subscriptions.participant_id
					WHERE
						participant_subscriptions.any_email = TRUE
				""")
				recipient_list = [ self._decrypt(row['email']) for row in rows ]
			elif recipient_group.lower() == "all":
				rows = self._connector.select("""
					SELECT
						email
					FROM
						participants
				""")
				recipient_list = [ self._decrypt(row['email']) for row in rows ]
			else:
				raise email_exceptions.UnknownRecipientGroupException(recipient_group)

			"""
			Add the given list of recipients to the email's recipients.
			"""
			if (recipients is not None and
				type(recipients) is list):
				recipient_list += recipients

			if len(recipient_list):
				self._connector.bulk_execute(
					"""
					INSERT INTO
						email_recipients (email_id, recipient)
					VALUES
						%s
					""",
					[ (email['id'], recipient) for recipient in recipient_list ],
					"(%s, %s)"
				)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "data": dict(email) })
		except (email_exceptions.UnknownRecipientGroupException,
				email_exceptions.UnsupportedRecipientGroupException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
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

		response = Response()

		try:
			id = int(id)

			if not self._email_exists(id):
				raise email_exceptions.EmailDoesNotExistException(id)

			"""
			Delete the email and associated recipients.
			"""
			self._connector.execute("""
				DELETE FROM
					emails
				WHERE
					id = %d
			""" % id)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (email_exceptions.EmailDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_email(self, id=None, recipients=False, search="", case_sensitive=False, number=-1, page=1, *args, **kwargs):
		"""
		Get the email with the given ID.
		If no ID is given, all emails are fetched.

		Associated recipients can also be fetched.

		:param id: The email's unique id.
		:type id: str
		:param recipients: A parameter that specifies whether the email's recipients should be returned.
		:type recipients: bool
		:param search: A search string used to look up emails using their subject and body.
		:type search: str
		:param case_sensitive: A boolean indicating whether the search should be case sensitive.
		:type case_sensitive: str
		:param number: The number of emails to retrieve.
			If a negative number is provided, all matching emails are retrieved.
		:type number: str
		:param page: The page number, used to aid in pagination.
		:type page: str

		:return: A response with any errors that may arise.
				 If an ID is provided, a single email is returned if found.
				 Otherwise, a list of emails is returned.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			if id is not None:
				id = int(id)

				if not self._email_exists(id):
					raise email_exceptions.EmailDoesNotExistException(id)

			number = int(number)
			page = max(int(page), 1)
			case_sensitive = case_sensitive == 'True'

			"""
			The base SQL string returns every email.
			The placeholder allows modifications to what is returned.
			"""
			sql = """
				SELECT
					emails.* %s
				FROM
					emails %s
				WHERE
					TRUE %s
			"""

			"""
			Complete the SELECT and FROM fields.
			"""
			"""
			If the recipients are requested, return them as well.
			"""
			if recipients:
				sql = sql % (
					", ARRAY_AGG(recipient) AS recipients",
					"""LEFT JOIN
						email_recipients
					ON
						emails.id = email_recipients.email_id""",
					'%s'
				)
			else:
				sql = sql % ('', '', '%s')

			"""
			Complete the WHERE field.
			"""
			filters = []

			"""
			Filter the emails if an ID is given.
			"""
			if id is not None:
				filters.append(f"id = {id}")

			"""
			Perform a search if a string is given.
			"""
			if search:
				filters.append(f"(emails.subject %s '%%{search}%%') OR (emails.body %s '%%{search}%%')"
				% ("LIKE" if case_sensitive else "ILIKE", "LIKE" if case_sensitive else "ILIKE"))

			if filters:
				sql = sql % ('AND ' + ' AND '.join(filters))
			else:
				sql = sql % ''

			"""
			Add grouping if recipients were requested.
			"""
			if recipients:
				sql += """
					GROUP BY
						emails.id
				"""

			"""
			Limit the results if a non-negative number is given.
			"""
			if number >= 0:
				sql += """
				LIMIT %d OFFSET %d""" % (
					number, number * (page - 1)
				)

			"""
			Get the response.
			"""
			emails = self._connector.select(sql)
			for i, email in enumerate(emails):
				emails[i]['created_at'] = emails[i]['created_at'].timestamp()

			"""
			Calculate the total number of results.
			"""
			sql = """
				SELECT
					COUNT(*) AS total
				FROM
					emails
				WHERE
					TRUE %s
			"""
			if filters:
				sql = sql % ('AND ' + ' AND '.join(filters))
			else:
				sql = sql % ''
			summary = self._connector.select_one(sql)

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "total": summary['total'], "data": emails[0] if id is not None else emails })
		except (email_exceptions.EmailDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def deliver(self, simulated=False, *args, **kwargs):
		"""
		Send the next unsent email.
		The `max_recipients` parameter can be used to limit the number of recipients to deliver to.

		:param simulated: A boolean to simulate the email delivery.
						 If the delivery is simulated, the email is not actually delivered, but marked as such.
		:type simulated: boolean

		:return: A response with any errors that may arise.
				 The email and the recipients to whom the email was sent are returned.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			"""
			Get the next email and its recipients.
			The results are returned in the same row.
			The recipients are returned as an array.
			"""

			email = self._get_next_email(*args, **kwargs)
			if email:
				recipients = email['recipients']
				email['created_at'] = email['created_at'].timestamp()
				del email['recipients']

				"""
				If there is an email to be sent, set up the SMTP connection.
				Then, set up the email itself and deliver it.
				The email is always sent to the sender, with the recipients being `Bcc` receivers.
				"""

				if not simulated:
					if smtp.smtp_secure == 'tls':
						smtpserver = smtplib.SMTP(smtp.smtp_host, smtp.smtp_port)
						smtpserver.set_debuglevel(0)
						smtpserver.ehlo()
						smtpserver.starttls()
						smtpserver.ehlo()
					elif smtp.smtp_secure == 'ssl':
						smtpserver = smtplib.SMTP_SSL(smtp.smtp_host, smtp.smtp_port)
						smtpserver.set_debuglevel(0)
						smtpserver.ehlo()

					"""
					Authenticate if need be.
					"""
					if smtp.smtp_auth:
						smtpserver.login(smtp.smtp_user, smtp.smtp_pass)

					"""
					Construct the email.
					"""
					message = MIMEText(email_partials.email() % email['body'], 'html')
					message['Subject'] = email['subject']
					message['From'] = f"{smtp.smtp_name} <{smtp.smtp_from}>"
					message['Bcc'] = ','.join(recipients)

					smtpserver.sendmail(smtp.smtp_from, [smtp.smtp_from] + recipients, message.as_string())
					smtpserver.close()

				"""
				Mark the emails as sent.
				"""

				self._connector.execute("""
					UPDATE
						email_recipients
					SET
						sent = True
					WHERE
						email_id = %d AND
						recipient IN ('%s')
				""" % (
					email['id'],
					"', '".join(recipients)
				))

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			if email:
				response.body = json.dumps({ 'data': { 'email': email, 'recipients': recipients } })
			else:
				response.body = json.dumps({ 'data': { } })
		except (email_exceptions.EmailDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			traceback.print_exc()
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def get_next_email(self, *args, **kwargs):
		"""
		Get the next unsent email.
		The `max_recipients` parameter can be used to limit the number of recipients to deliver to.

		:return: A response with any errors that may arise.
				 The email and the recipients to whom the email should be sent are returned.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			"""
			Get the next email and its recipients.
			The results are returned in the same row.
			The recipients are returned as an array.
			"""

			email = self._get_next_email(*args, **kwargs)
			if email:
				recipients = email['recipients']
				email['created_at'] = email['created_at'].timestamp()
				del email['recipients']

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			if email:
				response.body = json.dumps({ 'data': { 'email': email, 'recipients': recipients } })
			else:
				response.body = json.dumps({ 'data': { } })
		except (email_exceptions.EmailDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	"""
	Subscription functions.
	"""

	def get_subscription(self, username, subscription=None, *args, **kwargs):
		"""
		Get a participant's subscription status.
		If no subscription type is provided, all subscription types are returned.

		:param username: The username of the participant whose subscriptions will be retrieved.
		:type username: str
		:param subscription: The subscription to retrieve.
			If `None` is given, all subscriptions are returned.
		:type subscription: None or str

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			if subscription is not None and subscription not in self._get_subscription_types():
				raise email_exceptions.UnknownSubscriptionTypeException(subscription)

			"""
			Retrieve the subscription according to whether one or all subscriptions are requested.
			"""
			row = self._connector.select_one("""
				SELECT
					%s
				FROM
					participant_subscriptions
				WHERE
					participant_id = '%s'
			""" % (
				'*' if subscription is None else f"participant_id, {subscription}",
				username
			))

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ 'data': dict(row) })
		except (email_exceptions.UnknownSubscriptionTypeException,
				user_exceptions.ParticipantDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	def update_subscription(self, username, subscription, subscribed, *args, **kwargs):
		"""
		Update the subscription of a participant.

		:param username: The username of the participant whose subscription will be updated.
		:type username: str
		:param subscription: The subscription to update.
							 The only accepted subscription type at present is 'any_email'.
		:type subscription: str
		:param subscribed: A boolean indicating whether the participant is subscribed.
		:typr subscribed: bool

		:return: A response with any errors that may arise.
		:rtype: :class:`oauth2.web.Response`
		"""

		response = Response()

		try:
			username = self._sanitize(username)
			if not self._participant_exists(username):
				raise user_exceptions.ParticipantDoesNotExistException()

			if subscription not in self._get_subscription_types():
				raise email_exceptions.UnknownSubscriptionTypeException(subscription)

			"""
			Update the subscription.
			"""
			row = self._connector.execute("""
				UPDATE
					participant_subscriptions
				SET
					%s = %s
				WHERE
					participant_id = '%s'
			""" % (
				subscription, subscribed, username
			))

			response.status_code = 200
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ })
		except (email_exceptions.UnknownSubscriptionTypeException,
				user_exceptions.ParticipantDoesNotExistException) as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": str(e), "exception": e.__class__.__name__ })
		except Exception as e:
			response.status_code = 500
			response.add_header("Content-Type", "application/json")
			response.body = json.dumps({ "error": "Internal Server Error: %s" % str(e), "exception": e.__class__.__name__ })

		return response

	"""
	Supporting functions.
	"""

	def _email_exists(self, id):
		"""
		Check whether the email with the given ID exists.

		:param id: The email's unique id.
		:type id: str

		:return: A boolean indicating whether the email with the given ID exists.
		:rtype: bool
		"""

		return self._connector.exists("""
			SELECT
				*
			FROM
				emails
			WHERE
				id = %d
		""" % id)

	def _get_subscription_types(self):
		"""
		Get a list of supported subscription types.

		:return: A list of supported subscription types.
		:rtype: list of str
		"""

		"""
		No rows are retrieved. The important thing is to get the column names.
		"""
		schema = self._connector.select("""
			SELECT
				*
			FROM
				information_schema.columns
			WHERE
				table_schema = 'public' AND
				table_name   = 'participant_subscriptions'
		""")

		"""
		The `participant_id` column is not needed because it is not a subscription type.
		"""
		column_names = [ column['column_name'] for column in schema ]
		column_names = [ column for column in column_names if column != 'participant_id' ]
		return column_names

	def _get_next_email(self, max_recipients=-1, *args, **kwargs):
		"""
		Get the next unsent email.

		:param max_recipients: The maximum number of recipients to deliver the email to.
							   If a zero or negative number is provided, all participants are returned.
		:type max_recipients: int

		:return: The next email, or `None` if there is no unsent email.
				 The email and the recipients to whom the email was sent are returned.
		:rtype: dict or None
		"""

		sql = """
			SELECT
				emails.*, ARRAY_AGG(email_recipients.recipient) AS recipients
			FROM
				email_recipients JOIN emails
					ON email_recipients.email_id = emails.id
			WHERE
				email_recipients.sent = False
			GROUP BY
				emails.id
			ORDER BY
				id ASC
			LIMIT
				1
		"""

		"""
		Get the response.
		"""
		email = self._connector.select_one(sql)

		"""
		If a limit is imposed on the participants, return only the first few.
		"""
		max_recipients = int(max_recipients)
		if max_recipients > 0 and email is not None:
			email['recipients'] = email['recipients'][:max_recipients]

		return email
