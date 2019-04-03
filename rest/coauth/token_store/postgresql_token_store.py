"""
A token store that uses PostgreSQL.
"""

import psycopg2

from oauth2.error import AccessTokenNotFound
from oauth2.store.dbapi.mysql import MysqlAccessTokenStore, MysqlAuthCodeStore, MysqlClientStore

class PostgresqlAccessTokenStore(MysqlAccessTokenStore):
	"""
	The access token store that uses PostgreSQL.
	The implementation is based on MySQL since the two languages are similar.
	"""

	def __init__(self, connection):
		"""
		Initialize a new store class.
		It is assumed that the connection that is given is a database with the schema installed.

		:param connection: The database connection to use to store data.
		:type connection: :class:`connection.connection.Connection`
		"""
		self.connection = connection
		self.connection.reconnect()

	def save_token(self, access_token):
		"""
		Creates a new entry for an access token in the database.

		This is overriden because the returned `access_token_id` in the original function is invalid.
		The function uses `execute`, which itself returns `lastrowid`.
		For some reason, this row ID starts from 0, even though PostgreSQL starts row IDs from 1.
		Moreover, the auto increment starts from 1.
		Therefore there is a mismatch between the access token and its information (data and scope).
		Instead, the access token ID is fetched using a more secure way.

		:param access_token: An instance of an access token.
		:type access_token: :class:`oauth2.datatype.AccessToken`

		:return: `True`.
		:rtype: bool
		"""

		access_token_id = self.fetchone(self.create_access_token_query,
							access_token.client_id,
							access_token.grant_type,
							access_token.token,
							access_token.expires_at,
							access_token.refresh_token,
							access_token.refresh_expires_at,
							access_token.user_id)

		for key, value in list(access_token.data.items()):
			self.execute(self.create_data_query, key, value, access_token_id)

		for scope in access_token.scopes:
			self.execute(self.create_scope_query, scope, access_token_id)

		return True

	def fetch_by_token(self, access_token):
		"""
		Retrieves an access token by its token name.

		:param access_token: The name of an access token.
		:type access_token: str

		:return: The access token.
		:rtype: :class:`oauth2.datatype.AccessToken`

		:raises: :class:`oauth2.error.AccessTokenNotFound` if access token cannot be retrieved.
		"""
		row = self.fetchone(self.fetch_by_access_token_query, access_token)

		if row is None:
			raise AccessTokenNotFound

		scopes = self._fetch_scopes(access_token_id=row[0])

		data = self._fetch_data(access_token_id=row[0])

		return self._row_to_token(data=data, scopes=scopes, row=row)

	create_access_token_query = """
		SET TIME ZONE 'UTC';
		INSERT INTO access_tokens (
			client_id, grant_type, token, expires_at, refresh_token, refresh_expires_at, user_id
		) VALUES (
			%s, %s, %s, TO_TIMESTAMP(%s), '%s', TO_TIMESTAMP(%s), %s
		)
		RETURNING id"""

	create_scope_query = """
		INSERT INTO access_token_scopes (
			name, access_token_id
		) VALUES (
			%s, %s
		)"""

	fetch_by_access_token_query = """
		SELECT
			id, client_id, grant_type, token,
			EXTRACT(EPOCH FROM expires_at), refresh_token,
			EXTRACT(EPOCH FROM refresh_expires_at), user_id
		FROM
			access_tokens
		WHERE
			token = %s
		LIMIT 1"""

	fetch_data_by_access_token_query = """
		SELECT
		   key, value
		FROM
			access_token_data
		WHERE
			access_token_id = %s"""

	fetch_scopes_by_access_token_query = """
		SELECT
			name
		FROM
			access_token_scopes
		WHERE
			access_token_id = %s"""

class PostgresqlAuthCodeStore(MysqlAuthCodeStore):
	"""
	The authorization code store that uses PostgreSQL.
	The implementation is based on MySQL since the two languages are similar.
	"""

	pass

class PostgresqlClientStore(MysqlClientStore):
	"""
	The client store that uses PostgreSQL.
	The implementation is based on MySQL since the two languages are similar.
	"""

	pass
