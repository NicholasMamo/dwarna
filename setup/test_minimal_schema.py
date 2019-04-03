"""
Test the schema
The unit tests start off with a few fail-cases
Then, they move on to other cases that should succeed
"""

from abc import ABC, abstractmethod
from os.path import expanduser

import os
import psycopg2
import minimal_schema
import unittest

"""
The database that is used as a testing environment
"""
TEST_DATABASE = "testing_environment"

class User(ABC):

	def __init__(self, username):
		self._username = username

	def get_username(self):
		return self._username

	@abstractmethod
	def get_insertion_string(self):
		pass

class Participant(User):

	def get_insertion_string(self):
		return "'%s', '%s'" % (self._username, "PARTICIPANT")

class Biobanker(User):

	def get_insertion_string(self):
		return "'%s', '%s'" % (self._username, "BIOBANKER")

class Researcher(User):

	def get_insertion_string(self):
		return "'%s', '%s'" % (self._username, "RESEARCHER")

class Study():

	def __init__(self, name, description, homepage, start_date, end_date):
		self._name = name
		self._description = description
		self._homepage = homepage
		self._start_date = start_date
		self._end_date = end_date

	def set_id(self, id):
		self._id = id

	def get_id(self):
		return self._id

	def get_insertion_string(self):
		return "'%s', '%s', '%s', '%s', '%s'" % (self._name, self._description, self._homepage, self._start_date, self._end_date)

class SchemaTest(unittest.TestCase):
	"""
	Test the schema
	"""

	def __init__(self, *args, **kwargs):
		"""
		Connect with the database and save the cursor
		"""

		self.reconnect()
		super(SchemaTest, self).__init__(*args, **kwargs)

	def reconnect(self):
		"""
		Reconnect to the test database
		"""

		try:
			# get the connection details from the .pgpass file
			home = expanduser("~")
			with open(os.path.join(home, ".pgpass"), "r") as f:
				host, port, _, username, password = f.readline().strip().split(":")
				self._con = psycopg2.connect(dbname=TEST_DATABASE, user=username, host=host, password=password)
				self._cursor = self._con.cursor()
		except Exception as e:
			print(e)

	def assert_fail_sql(self, sql, exception_name):
		"""
		Assert that the given SQL code fails with the given exception
		At the end, reconnect with the database
		"""

		try:
			self._cursor.execute(sql)
		except Exception as e:
			self.assertEqual(type(e).__name__, exception_name)
		else:
			self.fail("Did not raise exception %s" % exception_name)
		finally:
			self.reconnect()

	def clear(self):
		"""
		Clear all the data from the database
		"""
		self._cursor.execute("DELETE FROM users")
		self._cursor.execute("DELETE FROM studies")
		self._cursor.execute("DELETE from attributes")
		self._con.commit()

	def test_users(self):
		"""
		Test user data
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

	def test_studies(self):
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
		study = Study("study", "lotsa work", "home", "2018-12-07", "2019-12-12")

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
			name, description, homepage, start_date, end_date)
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

	def test_attributes(self):
		"""
		Test attribute data
		"""

		print()
		print("Attribute tests")
		print("----------")

		self.clear()

		alice = Participant("al")
		john = Participant("jo")
		biobanker = Biobanker("biobanker")
		scientist = Researcher("re")
		study = Study("study", "lotsa work", "home", "2018-12-07", "2019-12-12")

		"""
		Insert some sample data into the database
		First, insert the study and fetch its ID
		"""
		self._cursor.execute("""INSERT INTO studies(
			name, description, homepage, start_date, end_date)
			VALUES (%s);""" % study.get_insertion_string());
		self._cursor.execute("""SELECT *
			FROM studies
			ORDER BY study_id DESC
			LIMIT 1;""")
		row = self._cursor.fetchone()
		study.set_id(row[0])

		"""
		Secondly, insert the users
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
		Save this basic data to return to it later after SQL failure tests
		"""
		self._con.commit()

		"""
		Misspelled enumeration name
		"""

		self.assert_fail_sql("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'BOOL')""", "DataError")

		"""
		Missing enumeration constraints
		"""
		self.assert_fail_sql("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'ENUMERATION')""", "IntegrityError")

		"""
		Test on composite primary key
		"""
		self._cursor.execute("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'BOOLEAN')""")
		self._cursor.execute("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'INTEGER')""")
		self.assert_fail_sql("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'BOOLEAN')""", "IntegrityError")

		"""
		Create some attributes and attach them to studies and participants
		"""
		self._cursor.execute("""SELECT *
			FROM attributes;""")
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""INSERT INTO attributes (
			name, type)
			VALUES ('Smoke', 'BOOLEAN')""")

		self._cursor.execute("""INSERT INTO studies_participants(
			study_id, participant_id)
			VALUES ('%d', '%s');""" % (study.get_id(), alice.get_username()))
		self._cursor.execute("""INSERT INTO participants_attributes(
			participant_id, attribute_name, attribute_type, value)
			VALUES ('%s', '%s', '%s', '%s');""" % (alice.get_username(), "Smoke", "BOOLEAN", "TRUE"))
		self._cursor.execute("""INSERT INTO studies_attributes(
			study_id, attribute_name, attribute_type)
			VALUES('%d', '%s', '%s');""" % (study.get_id(), "Smoke", "BOOLEAN"))
		self._con.commit()

		"""
		Test the composite primary keys of the participants_attributes and studies_attributes tables
		"""
		self.assert_fail_sql("""INSERT INTO participants_attributes(
			participant_id, attribute_name, attribute_type, value)
			VALUES ('%s', '%s', '%s', '%s');""" % (alice.get_username(), "Smoke", "BOOLEAN", "TRUE"), "IntegrityError")

		self.assert_fail_sql("""INSERT INTO studies_attributes(
			study_id, attribute_name, attribute_type)
			VALUES('%d', '%s', '%s');""" % (study.get_id(), "Smoke", "BOOLEAN"), "IntegrityError")

		"""
		Test the foreign key constraints
		"""
		self.assert_fail_sql("""INSERT INTO participants_attributes(
			participant_id, attribute_name, attribute_type, value)
			VALUES ('%s', '%s', '%s', '%s');""" % (alice.get_username(), "Smoke", "INTEGER", "10"), "IntegrityError")

		self.assert_fail_sql("""INSERT INTO participants_attributes(
			participant_id, attribute_name, attribute_type, value)
			VALUES ('%s', '%s', '%s', '%s');""" % (scientist.get_username(), "Smoke", "BOOLEAN", "TRUE"), "IntegrityError")

		self.assert_fail_sql("""INSERT INTO studies_attributes(
			study_id, attribute_name, attribute_type)
			VALUES('%d', '%s', '%s');""" % (study.get_id(), "Smoke", "INTEGER"), "IntegrityError")

		"""
		Test cascading deletion
		"""

		self._cursor.execute("""SAVEPOINT initial;""")

		"""
		Ensure that deleting a participant attribute row does not delete anything else
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants;""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))

		self._cursor.execute("""SELECT *
			FROM attributes
			WHERE name = '%s' AND
				type = '%s';""" % ('Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_attributes
			WHERE study_id = '%d' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Ensure that deleting a study attribute row does not delete anything else
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants;""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM studies_attributes
			WHERE study_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))

		self._cursor.execute("""SELECT *
			FROM attributes
			WHERE name = '%s' AND
				type = '%s';""" % ('Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_attributes
			WHERE study_id = '%d' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Ensure that deleting a study row deletes all of its associated attributes
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants;""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM studies
			WHERE study_id = '%d';""" % study.get_id())

		self._cursor.execute("""SELECT *
			FROM attributes
			WHERE name = '%s' AND
				type = '%s';""" % ('Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_attributes
			WHERE study_id = '%d' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))
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
		Ensure that deleting a participant row deletes all of its associated attributes
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants;""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM participants
			WHERE user_id = '%s';""" % alice.get_username())

		self._cursor.execute("""SELECT *
			FROM attributes
			WHERE name = '%s' AND
				type = '%s';""" % ('Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies_attributes
			WHERE study_id = '%d' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Ensure that deleting an attribute row only deletes attributes associated with studies and participants
		"""
		self._cursor.execute("ROLLBACK TO SAVEPOINT initial")

		# confirm the rollback
		self._cursor.execute("""SELECT *
			FROM studies_participants;""")
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""DELETE FROM attributes
			WHERE name = '%s' AND type = '%s';""" % ('Smoke', 'BOOLEAN'))

		self._cursor.execute("""SELECT *
			FROM attributes
			WHERE name = '%s' AND
				type = '%s';""" % ('Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies
			WHERE study_id = '%d';""" % study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM participants_attributes
			WHERE participant_id = '%s' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (alice.get_username(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies_attributes
			WHERE study_id = '%d' AND
				attribute_name = '%s' AND
				attribute_type = '%s';""" % (study.get_id(), 'Smoke', 'BOOLEAN'))
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""SELECT *
			FROM studies_participants
			WHERE study_id = '%d' AND participant_id = '%s';""" % (study.get_id(), alice.get_username()))
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""SELECT *
			FROM users, participants
			WHERE users.user_id = participants.user_id AND users.user_id = '%s';""" % alice.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

def create_testing_environment():
	"""
	Create a testing environment so that the used database is not altered
	"""

	# get the connection details from the .pgpass file
	home = expanduser("~")
	with open(os.path.join(home, ".pgpass"), "r") as f:
		host, port, database, username, password = f.readline().strip().split(":")
		con = psycopg2.connect(dbname=database, user=username, host=host, password=password)

		con.autocommit = True # commit all changes automatically
		cursor = con.cursor() # fetch the cursor

		"""
		Ensure that the database does not already exist
		Create it only if it doesn't exist
		"""
		cursor.execute("""SELECT 1 FROM pg_database WHERE datname = '%s'""" % TEST_DATABASE)
		print("Database has to be created" if not cursor.rowcount else "Database already exists")
		if (cursor.rowcount == 0):
			cursor.execute("CREATE DATABASE %s" % TEST_DATABASE)
		minimal_schema.create_schema(TEST_DATABASE)

if __name__ == "__main__":
	"""
	First create the testing environment, then perform the unit tests
	"""

	create_testing_environment()
	unittest.main()
