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

from .environment import *
from .models import *
from .test import SchemaTestCase

class UserTests(SchemaTestCase):
	"""
	Test the user schema.
	"""

	def test_users(self):
		"""
		Test user data.
		"""

		clear()
		participant = Participant("participant")
		biobanker = Biobanker("biobanker")
		researcher = Researcher("researcher")

		"""
		The database should be empty by now
		"""
		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Therefore biobankers, researchers and participants cannot be inserted
		Each time, an IntegrityError should be raised because the ForeignKey constraint is not respected
		"""
		self.assert_fail_sql("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
			""" % biobanker.get_username(), "IntegrityError")
		self.assert_fail_sql("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username(), "IntegrityError")
		self.assert_fail_sql("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username(), "IntegrityError")

	def test_user_type_enumeration(self):
		"""
		The user role is an enumeration, and it cannot be violated.
		This is incorrect data, hence the DataError violation.
		"""

		clear()

		self.assert_fail_sql("""
			INSERT INTO
				users (user_id, role)
			VALUES
				('t_id', 'ADMIN');""", "DataError")

	def test_inserting_duplicate_user(self):
		"""
		There may be no duplicate users.
		This forces an IntegrityError.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())

		self.assert_fail_sql("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string(), "IntegrityError")

	def test_inserting_duplicate_biobanker(self):
		"""
		Biobankers must be unique.
		Otherwise, an IntegrityError is raised.
		"""

		clear()
		biobanker = Biobanker("biobanker")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % biobanker.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % biobanker.get_username())
		self.assert_fail_sql("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % biobanker.get_username(), "IntegrityError")

	def test_inserting_duplicate_researcher(self):
		"""
		Researchers must be unique.
		Otherwise, an IntegrityError is raised.
		"""

		clear()
		researcher = Researcher("researcher")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % researcher.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username())
		self.assert_fail_sql("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username(), "IntegrityError")

	def test_inserting_duplicate_participant(self):
		"""
		Participants must be unique.
		Otherwise, an IntegrityError is raised.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username())
		self.assert_fail_sql("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username(), "IntegrityError")

	def test_insert_user(self):
		"""
		Insert a single user into the database.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 1)

	def test_delete_user(self):
		"""
		Delete a user from the database.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE
				user_id = '%s'
		""" % participant.get_username())
		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_delete_all_users(self):
		"""
		Delete all users from the database.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE TRUE;
		""")
		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_insert_biobanker(self):
		"""
		Insert a biobanker into the database.
		"""

		clear()
		biobanker = Biobanker("biobanker")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % biobanker.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % biobanker.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				users, biobankers
			WHERE
				users.user_id = biobankers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

	def test_remove_biobanker_from_users(self):
		"""
		Remove a biobanker from the users table.
		The user should also be removed from the biobankers table at the same time.
		"""

		clear()
		biobanker = Biobanker("biobanker")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % biobanker.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % biobanker.get_username())

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE
				user_id = '%s'""" % biobanker.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				biobankers""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				biobankers""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_remove_biobanker_from_biobankers(self):
		"""
		Remove a biobanker from the biobankers table.
		The user should also be removed from the users table at the same time.
		"""

		clear()
		biobanker = Biobanker("biobanker")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % biobanker.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % biobanker.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				users, biobankers
			WHERE
				users.user_id = biobankers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			DELETE FROM
				biobankers
			WHERE
				user_id = '%s'
		""" % biobanker.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				biobankers""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_insert_researcher(self):
		"""
		Insert a researcher into the database.
		"""

		clear()
		researcher = Researcher("researcher")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % researcher.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username())
		self._cursor.execute("""
			SELECT *
			FROM
				users, researchers
			WHERE
				users.user_id = researchers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

	def test_remove_researcher_from_users(self):
		"""
		Remove a researcher from the users table.
		The user should also be removed from the researchers table at the same time.
		"""

		clear()
		researcher = Researcher("researcher")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % researcher.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username())

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE
				user_id = '%s'""" % researcher.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				researchers""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				researchers""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_remove_researcher_from_researchers(self):
		"""
		Remove a researcher from the researchers table.
		The user should also be removed from the users table at the same time.
		"""

		clear()
		researcher = Researcher("researcher")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % researcher.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % researcher.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				users, researchers
			WHERE
				users.user_id = researchers.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			DELETE FROM
				researchers
			WHERE
				user_id = '%s'
		""" % researcher.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				researchers""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_insert_participant(self):
		"""
		Insert a participant into the database.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username())
		self._cursor.execute("""
			SELECT *
			FROM
				users, participants
			WHERE
				users.user_id = participants.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

	def test_remove_participant_from_users(self):
		"""
		Remove a participant from the users table.
		The user should also be removed from the participants table at the same time.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username())

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE
				user_id = '%s'""" % participant.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				participants""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				participants""")
		self.assertEqual(self._cursor.rowcount, 0)

	def test_remove_participant_from_participants(self):
		"""
		Remove a participant from the participants table.
		The user should also be removed from the users table at the same time.
		"""

		clear()
		participant = Participant("participant")

		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s);
		""" % participant.get_insertion_string())
		self._cursor.execute("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s');
		""" % participant.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				users, participants
			WHERE
				users.user_id = participants.user_id""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			DELETE FROM
				participants
			WHERE
				user_id = '%s'
		""" % participant.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				participants""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				users""")
		self.assertEqual(self._cursor.rowcount, 0)
