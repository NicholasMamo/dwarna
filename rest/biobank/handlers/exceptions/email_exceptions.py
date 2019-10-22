"""
Exceptions about emails.
"""

class EmailDoesNotExistException(Exception):
	"""
	An exception that indicates that an email that is sought does not exist.
	"""

	def __init__(self, id, message="The email with ID %d does not exist"):
		super(EmailDoesNotExistException, self).__init__(message % id)

class UnknownRecipientGroupException(Exception):
	"""
	An exception that indicates that the given recipient group is not known.
	"""

	def __init__(self, recipient_group, message="Recipient group '%s' is unknown"):
		super(UnknownRecipientGroupException, self).__init__(message % recipient_group)

class UnsupportedRecipientGroupException(Exception):
	"""
	An exception that indicates that the given recipient group is not supported.
	"""

	def __init__(self, recipient_group, message="Recipient group '%s' is not supported"):
		super(UnsupportedRecipientGroupException, self).__init__(message % recipient_group)

class UnknownSubscriptionTypeException(Exception):
	"""
	An exception that indicates that the given subscription type is not known.
	"""

	def __init__(self, subscription, message="Subscription type '%s' is unknown"):
		super(UnknownSubscriptionTypeException, self).__init__(message % subscription)
