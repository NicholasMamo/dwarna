database = "biobank"
"""
:var database: The database used by default.
:vartype database: str
"""

oauth_database = "biobank_oauth"
"""
:var database: The OAuth database used by default.
:vartype database: str
"""

encryption_secret = b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
"""
:var encryption_secret: The secret key used to encrypt and decrypt.
						To generate a new secret run:

						.. code-block:: python

							from cryptography.fernet import Fernet
							key = Fernet.generate_key()

:vartype encryption_secret: bytes
"""
