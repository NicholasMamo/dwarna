"""
Exceptions that arise from Ethereum tasks.
"""

def get_error_msg(error_msg):
	"""
	Returns the error message from a web3 exception

	:param username: The exception thrown when sending a transaction on chain.
	:type error_msg: class web3 exception

	:return: The error message returned from a require() in the smart contract.
	:rtype: str
	"""

	error = error_msg.split("execution reverted: ",1)[1]
	print("Error: ", error)
	return error

class CreateStudyFailedException(Exception):
	"""
	An exception that indicates that the transaction to create a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(CreateStudyFailedException, self).__init__(message)

class AddConsentToStudyFailedException(Exception):
	"""
	An exception that indicates that the transaction to add a consent to a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(AddConsentToStudyFailedException, self).__init__(message)

class WithdrawConsentFromStudyFailedException(Exception):
	"""
	An exception that indicates that the transaction to withdraw a consent from a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(WithdrawConsentFromStudyFailedException, self).__init__(message)

class HasConsentedFailedException(Exception):
	"""
	An exception that indicates that the transaction to check if a participant has consented a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(HasConsentedFailedException, self).__init__(message)

class GetAllStudyParticipantsFailedException(Exception):
	"""
	An exception that indicates that the transaction to get all the participants of a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(GetAllStudyParticipantsFailedException, self).__init__(message)

class GetConsentingParticipantsFailedException(Exception):
	"""
	An exception that indicates that the transaction to get the consenting participants of a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(GetConsentingParticipantsFailedException, self).__init__(message)

class GetConsentTrailFailedException(Exception):
	"""
	An exception that indicates that the transaction to get the comsent trail of a participant of a study failed.
	"""

	def __init__(self, message=f"%s"):
		super(GetConsentTrailFailedException, self).__init__(message)
