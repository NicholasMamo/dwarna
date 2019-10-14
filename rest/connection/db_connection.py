"""
Database interfaces using the base connection class.
"""

import os
from os.path import expanduser

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
	:ivar _con: The connection to the PostgreSQL database.
	:vartype _con: :class:`psycopg2.extensions.connection`
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

	@staticmethod
	def connect(database, *args, **kwargs):
		"""
		Connect to the given database by looking for the credentials in the .pgpass file.

		Additional arguments to the :class:`connection.db_connection.PostgreSQLConnection` can be passed.

		:param database: The name of the database to connect to.
		:type database: str

		:return: The database connection.
		:rtype: :class:`connection.db_connection.PostgreSQLConnection`
		"""

		home = expanduser("~")
		with open(os.path.join(home, ".pgpass"), "r") as file:
			"""
			Go through each line in the .pgpass file.
			Extract the connection details from the line.
			"""
			for i, line in enumerate(file):
				host, port, db, username, password = line.strip().split(":")

				"""
				If the line belongs to the requested database, create the connection.
				Then, return immediately.
				"""
				if db == database:
					return PostgreSQLConnection(db, host, username, password, *args, **kwargs)

		# TODO: what if it fails?

	def reconnect(self):
		"""
		Reconnect to the database.
		"""

		self._con = psycopg2.connect(dbname=self._database, host=self._host, user=self._username, password=self._password)

	def cursor(self):
		"""
		Fetch the connection's cursor.

		:return: A cursor for the connection.
		:rtype: :class:`DictCursorBase`
		"""

		cursor = self._con.cursor(cursor_factory=self._cursor_factory)

		return cursor

	def commit(self):
		"""
		Commit the changes.
		"""

		self._con.commit()

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

		cursor = self.execute(query, with_cursor=True)
		try:
			results = cursor.fetchall()
		except psycopg2.ProgrammingError:
			return self.exists(query)
		finally:
			cursor.close()
		return len(results) > 0

	def select_one(self, query):
		"""
		Fetch one row from the database.

		:param query: The `select` query to execute.
		:type query: str

		:return: A single row.
		:rtype: dict
		"""

		cursor = self.execute(query, with_cursor=True)
		row = cursor.fetchone()
		cursor.close()
		return row

	def select(self, query):
		"""
		Fetch all the rows returned from the database using the given query.

		:param query: The `select` query to execute.
		:type query: str

		:return: All the rows returned by the query.
		:rtype: list
		"""

		cursor = self.execute(query, with_cursor=True)
		rows = cursor.fetchall()
		cursor.close()
		return rows

	def execute(self, batch, with_cursor=False):
		"""
		Execute the given transactions. If one fails, roll back all the changes.
		This function does not return anything, but it may throw exceptions.
		When something does go awry, the connection establishes a new connection.

		If the execution is supposed to return results, then the `with_cursor` parameter returns the used cursor.
		Otherwise, the used cursor is closed.

		:param batch: A batch of queries to execute.
		:type batch: list of str

		:return: A cursor with the results.
		:rtype: None or :class:`DictCursorBase`

		:raises: :class:`Exception`: Any exception that is caught is rethrown.
		"""

		try:
			cursor = self.cursor()

			"""
			The transactions are only committed if all of them are successful.
			"""
			if type(batch) == list:
				for query in batch:
					cursor.execute(query)
			else:
				cursor.execute(batch)
			self._con.commit()

			if with_cursor:
				return cursor
			else:
				cursor.close()
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
