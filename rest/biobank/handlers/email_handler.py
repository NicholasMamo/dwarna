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

	pass
