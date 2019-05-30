"""
Test the study schema.
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

class StudyTests(SchemaTestCase):
	"""
	Test the study schema.
	"""

	def no_test_studies(self):
		"""
		Test study data
		"""

		print()
		print("Study tests")
		print("----------")

		self.clear()

		alice = Participant("al")
		john = Participant("jo")
		biobanker = Biobanker("biobanker")
		scientist = Researcher("re")
		study = Study("study", "lotsa work", "home")

		"""
		Insert some sample data into the database
		First, insert the users
		"""
		self._cursor.execute("""INSERT INTO users (
			user_id, role)
			VALUES (%s), (%s), (%s), (%s);""" % (alice.get_insertion_string(),
													john.get_insertion_string(),
													biobanker.get_insertion_string(),
													scientist.get_insertion_string()))

		self._cursor.execute("""INSERT INTO participants (
			user_id)
			VALUES ('%s'), ('%s');""" % (alice.get_username(), john.get_username()))

		self._cursor.execute("""INSERT INTO researchers (
			user_id)
			VALUES ('%s');""" % scientist.get_username())

		self._cursor.execute("""INSERT INTO biobankers (
			user_id)
			VALUES ('%s');""" % biobanker.get_username())

		"""
		Secondly, create a simple study and fetch its ID
		"""
		self._cursor.execute("""INSERT INTO studies(
			name, description, homepage)
			VALUES (%s);""" % study.get_insertion_string());

		self._cursor.execute("""SELECT *
			FROM studies
			ORDER BY study_id DESC
			LIMIT 1;""")
		row = self._cursor.fetchone()
		study.set_id(row[0])

		"""
		Save this basic data to return to it later after SQL failure tests
		"""
		self._con.commit()

		"""
		Only participants may be added to the study
		"""
		self.assert_fail_sql("""INSERT INTO studies_participants(
			study_id, participant_id)
			VALUES ('%d', '%s')""" % (study.get_id(), biobanker.get_username()), "IntegrityError")
		self.assert_fail_sql("""INSERT INTO studies_participants(
			study_id, participant_id)
			VALUES ('%d', '%s')""" % (study.get_id(), scientist.get_username()), "IntegrityError")

		"""
		The study ID must be valid
		"""
		self.assert_fail_sql("""INSERT INTO studies_participants(
			study_id, participant_id)
			VALUES ('%d', '%s')""" % (-1, alice.get_username()), "IntegrityError")

		"""
		The default consent value should be false
		"""
		self._cursor.execute("""INSERT INTO studies_participants(
			study_id, participant_id)
			VALUES ('%d', '%s')""" % (study.get_id(), alice.get_username()))

		self._cursor.execute("""SELECT consent
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s'""" % (study.get_id(), alice.get_username()))
		consent = self._cursor.fetchone()[0]

		"""
		Test updating the consent
		"""
		self._cursor.execute("""UPDATE studies_participants
			SET consent = True
			WHERE study_id = '%d' AND participant_id = '%s'""" % (study.get_id(), alice.get_username()))

		self._cursor.execute("""SELECT consent
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s'""" % (study.get_id(), alice.get_username()))
		consent = self._cursor.fetchone()[0]
		self.assertTrue(consent)

		"""
		Test cascading deletion
		"""

		"""
		Ensure that deleting a consent row does not delete anything else
		"""
		self._cursor.execute("""SAVEPOINT initial;""")
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Ensure that deleting a study deletes associated consent rows, but not participants
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM studies
			WHERE study_id = '%d';""" % study.get_id())

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Ensure that deleting a participant deletes associated consent rows, but not studies
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM participants
			WHERE user_id = '%s';""" % alice.get_username())

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Ensure that deleting a user deletes associated consent rows, but not studies
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM users
			WHERE user_id = '%s';""" % alice.get_username())

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)
