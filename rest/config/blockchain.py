host = "http://localhost"
"""
:var host: The URL where the Hyperledger Composer REST API is hosted.
:vartype host: str
"""

admin_port = 3001
"""
:var admin_port: The port where the Hyperledger Composer REST API listens to admin requests.
:vartype admin_port: int
"""

multiuser_port = 3000
"""
:var multiuser_port: The port where the Hyperledger Composer REST API listens to multi-user requests.
:vartype multiuser_port: int
"""

multi_card = False
"""
:var multi_card: A flag that determines whether a multi-card workflow is followed.
				 If set to true, then each participant will have one identity for each study that they ever participate in.
				 Otherwise, a new identity is generated the first time they participate in a study.
				 Later, the same identity would be used over and over again.
:vartype multi_card: bool
"""
