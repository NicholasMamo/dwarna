from .routes import *

"""
Build the list of possible scopes from the routes.
"""

default_scope = "none"
"""
:var default_scope: The default scope of access tokens.
	It should permit no data access whatsoever, except to functions that require no scopes.
:vartype default_scope: str
"""

scopes = [ scope for route in routes.values()
			for handler in route.values()
			for scope in handler["scopes"] ]
scopes.append(default_scope)
scopes.append(admin_scope)
scopes = list(set(scopes))
"""
:var scopes: All the possible scopes given by the authoization server.
:vartype scopes: list
"""

token_expiry = 120
"""
:var token_expiry: How long (in seconds) access tokens should live before being retired.
:vartype token_expiry: int
"""

client_id = '2d7db5ed5ca043c68cc9ff01f405a930'
"""
:var client_id: The client ID for the OAuth 2.0 Client Credentials workflow.
				The client ID can be based on a `UUID <https://www.ietf.org/rfc/rfc4122.txt>`_.
				By default, the database expects a 32-character string. Therefore the dashes are removed.
				To generate a UUID:

                .. code-block:: python

				   import uuid
				   str(uuid.uuid4()).replace('-', '')

:vartype client_id: str
"""

client_secret = 'Y41uqXoj9FMfK4D3cTmTxEZr0oB7Eisi'
"""
:var client_secret: The client secret for the OAuth 2.0 Client Credentials workflow.
					The string length can be up to 32 characters by default.
					To generate a secret:

					.. code-block:: python

					   import random
					   import string
					   ''.join(random.choice(string.ascii_letters + string.digits) for i in range(0, 32))
:vartype client_secret: str
"""
