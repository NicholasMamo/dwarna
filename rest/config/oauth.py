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

oauth_database = "biobank_oauth"
"""
:var database: The OAuth database used by default.
:vartype database: str
"""
