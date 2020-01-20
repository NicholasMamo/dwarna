admin_host = "http://localhost"
"""
:var admin_host: The URL where the Hyperledger Composer admin REST API is hosted, without trailing slash.
:vartype admin_host: str
"""

admin_port = 3001
"""
:var admin_port: The port where the Hyperledger Composer REST API listens to admin requests.
				 If the port is `None`, it is not used.
				 Only the users with the 'admin' scope can use this port.
:vartype admin_port: int or None
"""

multiuser_host = "http://localhost"
"""
:var multiuser_host: The URL where the Hyperledger Composer multi-user REST API is hosted, without trailing slash.
:vartype multiuser_host: str
"""

multiuser_port = 3000
"""
:var multiuser_port: The port where the Hyperledger Composer REST API listens to multi-user requests.
					 If the port is `None`, it is not used.
:vartype multiuser_port: int or None
"""

multi_card = True
"""
:var multi_card: A flag that determines whether a multi-card workflow is followed.
				 If set to true, then each participant will have one identity for each study that they ever participate in.
				 Otherwise, a new identity is generated the first time they participate in a study.
				 Later, the same identity would be used over and over again.
:vartype multi_card: bool
"""
