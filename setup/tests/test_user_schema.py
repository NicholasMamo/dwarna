"""
Test the user schema.
"""

import sys
import os

from os.path import expanduser

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import os
import psycopg2
import minimal_schema
import unittest

from environment import *
from models import *
from test import SchemaTestCase

class UserTests(SchemaTestCase):
	"""
	Test the user schema.
	"""

	def test_users(self):
		"""
		Test user data.
		"""

		print()
		print("User tests")
		print("----------")

		self.clear()

		alice = Participant("al")
		john = Participant("jo")
		biobanker = Biobanker("biobanker")
		scientist = Researcher("re")

		"""
		The database should be empty by now
		"""
		self._cursor.execute("""SELECT * FROM users""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Therefore biobankers, researchers and participants cannot be inserted
		Each time, an IntegrityError should be raised because the ForeignKey constraint is not respected
		"""
		self.assert_fail_sql("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % biobanker.get_username(), "IntegrityError")
		self.assert_fail_sql("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % scientist.get_username(), "IntegrityError")
		self.assert_fail_sql("""INSERT INTO participants (
			user_id)
			VALUES ('%s');""" % alice.get_username(), "IntegrityError")

		"""
		The user role is an enumeration, and it cannot be violated
		This is incorrect data, hence the DataError violation
		"""
		self.assert_fail_sql("""INSERT INTO users (
			user_id, role)
			VALUES ('t_id', 'ADMIN');""", "DataError")

		"""
		There may be no duplicate users
		This forces an IntegrityError
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self.assert_fail_sql("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string(), "IntegrityError")

		"""
		Biobankers, researchers and participants must be unique
		Otherwise, an IntegrityError is raised
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % alice.get_username())
		self.assert_fail_sql("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % alice.get_username(), "IntegrityError")

		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % alice.get_username())
		self.assert_fail_sql("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % alice.get_username(), "IntegrityError")

		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""INSERT INTO participants (
			user_id)
			VALUES ('%s');""" % alice.get_username())
		self.assert_fail_sql("""INSERT INTO participants (
			user_id)
			VALUES ('%s');""" % alice.get_username(), "IntegrityError")

		self.clear()

		"""
		Insert a single user into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""SELECT * FROM users""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Delete all users
		"""
		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s'""" % alice.get_username())
		self._cursor.execute("""SELECT *
			FROM users""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a biobanker into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % biobanker.get_insertion_string())
		self._cursor.execute("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % biobanker.get_username())
		self._cursor.execute("""SELECT *
			FROM users, biobankers
			WHERE users.user_id = biobankers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a biobanker from the users table
		"""
		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s'""" % biobanker.get_username())
		self._cursor.execute("""SELECT *
			FROM biobankers""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a biobanker into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % biobanker.get_insertion_string())
		self._cursor.execute("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % biobanker.get_username())
		self._cursor.execute("""SELECT *
			FROM users, biobankers
			WHERE users.user_id = biobankers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a biobanker from the biobankers table
		"""
		self._cursor.execute("""DELETE FROM biobankers
			WHERE user_id = '%s'""" % biobanker.get_username())
		self._cursor.execute("""SELECT *
			FROM users""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a researcher into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % scientist.get_insertion_string())
		self._cursor.execute("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % scientist.get_username())
		self._cursor.execute("""SELECT *
			FROM users, researchers
			WHERE users.user_id = researchers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a researcher from the users table
		"""
		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s'""" % scientist.get_username())
		self._cursor.execute("""SELECT *
			FROM researchers""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a researcher into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % scientist.get_insertion_string())
		self._cursor.execute("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % scientist.get_username())
		self._cursor.execute("""SELECT *
			FROM users, researchers
			WHERE users.user_id = researchers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a researcher from the researchers table
		"""
		self._cursor.execute("""DELETE FROM researchers
			WHERE user_id = '%s'""" % scientist.get_username())
		self._cursor.execute("""SELECT *
			FROM users""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a participant into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""INSERT INTO participants (
			user_id)
			VALUES ('%s');""" % alice.get_username())
		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a participant from the users table
		"""
		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s'""" % alice.get_username())
		self._cursor.execute("""SELECT *
			FROM participants""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Insert a participant into the database
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s);""" % alice.get_insertion_string())
		self._cursor.execute("""INSERT INTO participants (
			user_id)
			VALUES ('%s');""" % alice.get_username())
		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Remove a participant from the participants table
		"""
		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s'""" % alice.get_username())
		self._cursor.execute("""SELECT *
			FROM users""")
		self.assertEqual(self._cursor.rowcount, 0)
