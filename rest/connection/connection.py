"""
The connection to the PostgreSQL, which also executes commands on behalf of applications.
"""

from abc import ABC, abstractmethod, abstractstaticmethod

class Connection(ABC):
	"""
	A generic connection class
	"""

	@abstractstaticmethod
	def connect(database, *args, **kwargs):
		"""
		Connect to the database having the given name.
		The function should return the connection object wrapped in the class.

		:param database: The name of the database to connect to.
		:type database: str

		:return: The database connection.
		:rtype: :class:`connection.db_connection.Connection`
		"""

		pass
