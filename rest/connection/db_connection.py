"""
Database interfaces using the base connection class.
"""

import psycopg2
import psycopg2.extras

from .connection import Connection

class PostgreSQLConnection(object):
	"""
	The connection to the PostgreSQL database.

	:ivar _database: The name of the database to which a connection will be established.
	:vartype _database: str
	:ivar _host: The hostname where the database resides.
	:vartype _host: str
	:ivar _username: The username used to connect to the database.
	:vartype _username: str
	:ivar _password: The password used to connect to the database
	:vartype _password: str
	:ivar _cursor_factory: The type of cursors to create.
		The RealDictCursor factory is the default one.
		This factory returns associative arrays (`dict` instances) from queries.
	:type _cursor_factory: :class:`psycopg2.extras.RealDictCursor`
	"""

	def __init__(self, database, host, username, password, cursor_factory=psycopg2.extras.RealDictCursor):
		"""
		Save the credentials used to connect to the database and establish a connection.

		:param database: The name of the database to which a connection will be established.
		:type database: str
		:param host: The hostname where the database resides.
		:type host: str
		:param username: The username used to connect to the database.
		:type username: str
		:param password: The password used to connect to the database
		:type password: str
		:param cursor_factory: The type of cursors to create.
			The RealDictCursor factory is the default one.
			This factory returns associative arrays (`dict` instances) from queries.
		:type cursor_factory: :class:`psycopg2.extras.RealDictCursor`
		"""

		self._database = database
		self._host = host
		self._username = username
		self._password = password
		self._cursor_factory = cursor_factory

		self.reconnect()

	def reconnect(self):
		"""
		Reconnect to the database.
		"""

		try:
			self._con = psycopg2.connect(dbname=self._database, host=self._host, user=self._username, password=self._password)
			self._cursor = self._con.cursor(cursor_factory=self._cursor_factory)
		except Exception as e:
			print(e)

	def commit(self):
		"""
		Commit the changes.
		"""

		self._con.commit()

	def cursor(self):
		"""
		Fetch the connection's cursor.
		"""

		return self._con.cursor(cursor_factory=self._cursor_factory)

	def count(self, query):
		"""
		Count the number of rows when executing the given query.
		The COUNT command itself has to be given.
		This function only acts as a wrapper, getting just a number of rows.

		:param query: The query to execute.
		:type query: str

		:return: The number of rows in the query.
		:rtype: int
		"""

		return self.select_one(query)["count"]

	def exists(self, query):
		"""
		Check whether the query returns any rows.
		The query should be a `select` statement.

		:param query: The query to execute.
		:type query: str

		:return: A boolean indicating whether any rows were returned from the query.
		:rtype: bool
		"""

		self.execute(query)
		try:
			results = self._cursor.fetchall()
		except psycopg2.ProgrammingError:
			return self.exists(query)
		return len(results) > 0

	def select_one(self, query):
		"""
		Fetch one row from the database.

		:param query: The `select` query to execute.
		:type query: str

		:return: A single row.
		:rtype: dict
		"""

		self.execute(query)
		return self._cursor.fetchone()

	def select(self, query):
		"""
		Fetch all the rows returned from the database using the given query.

		:param query: The `select` query to execute.
		:type query: str

		:return: All the rows returned by the query.
		:rtype: list
		"""

		self.execute(query)
		return self._cursor.fetchall()

	def execute(self, batch):
		"""
		Execute the given transactions. If one fails, roll back all the changes.
		This function does not return anything, but it may throw exceptions.
		When something does go awry, the connection establishes a new connection.

		:param batch: A batch of queries to execute.
		:type batch: list of str

		:raises: :class:`Exception`: Any exception that is caught is rethrown.
		"""

		try:
			"""
			The transactions are only committed if all of them are successful.
			"""
			if type(batch) == list:
				for query in batch:
					self._cursor.execute(query)
			else:
				self._cursor.execute(batch)
			self._con.commit()
		except Exception as e:
			"""
			If the transactions failed for some reason, reconnect to the database and raise the exception again.
			In this way, the calling function knows about the failure.
			"""
			self.reconnect()
			raise e

	def close(self):
		"""
		Close the connection.
		"""

		self._con.close()
		print("PostgreSQL connection closed")

	def copy(self):
		"""
		Duplicate the connection.
		This can be used to create a different session.

		:return: The new connection.
		:rtype: :class:`connection.db_connection.PostgreSQLConnection`
		"""

		return PostgreSQLConnection(self._database, self._host, self._username, self._password, self._cursor_factory)
