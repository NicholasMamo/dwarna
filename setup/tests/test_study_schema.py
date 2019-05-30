"""
Test the study schema.
"""

import os
import sys

from functools import wraps
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

class StudyTests(SchemaTestCase):
	"""
	Test the study schema.
	"""

	@classmethod
	def setUpClass(self):
		"""
		Set up the class to create the schema.
		"""

		super(StudyTests, self).setUpClass()

	def __init__(self, *args, **kwargs):
		"""
		On initialization, generate some test data.
		"""

		super(StudyTests, self).__init__(*args, **kwargs)

		clear()

		self._participant_1 = Participant("participant_1")
		self._participant_2 = Participant("participant_2")
		self._biobanker = Biobanker("biobanker")
		self._researcher = Researcher("researcher")
		self._study = Study("2320", "study", "test study", "http://um.edu.mt/")

	def generate_data(self):
		"""
		Insert the sample data into the database.
		First, insert the users.
		"""
		self._cursor.execute("""
			INSERT INTO
				users (user_id, role)
			VALUES
				(%s), (%s), (%s), (%s);
		""" % (
			self._participant_1.get_insertion_string(),
			self._participant_2.get_insertion_string(),
			self._biobanker.get_insertion_string(),
			self._researcher.get_insertion_string()
		))

		self._cursor.execute("""
			INSERT INTO
				participants (user_id)
			VALUES
				('%s'), ('%s');
		""" % (
			self._participant_1.get_username(),
			self._participant_2.get_username()
		))

		self._cursor.execute("""
			INSERT INTO
				researchers (user_id)
			VALUES
				('%s');
		""" % self._researcher.get_username())

		self._cursor.execute("""
			INSERT INTO
				biobankers (user_id)
			VALUES
				('%s');
		""" % self._biobanker.get_username())

		"""
		Secondly, create a simple study and fetch its ID
		"""
		self._cursor.execute("""
			INSERT INTO
				studies (study_id, name, description, homepage)
			VALUES
				(%s);
		""" % self._study.get_insertion_string());

		"""
		Save this basic data to return to it later after SQL failure tests.
		"""
		self._con.commit()

	def isolated_test(test):
		"""
		Perform the test in isolation.
		In essence, this means that the data is cleared from the database.
		Then, sample data is re-introduced.

		:param test: The test to perform.
		:type test: function
		"""

		@wraps(test)

		def wrapper(*args):
			"""
			The wrapper first removes all data from the database.
			Then, it generates new data and calls the test.
			"""

			clear()
			self = args[0]
			self.generate_data()
			test(*args)

		return wrapper

	@isolated_test
	def test_add_biobanker_to_study(self):
		"""
		Only researchers may be added to the study.
		Thus, adding a biobanker to a study should fail because the foreign key won't match.
		"""

		self.assert_fail_sql("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._biobanker.get_username()
		), "ForeignKeyViolation")

	@isolated_test
	def test_add_participant_to_study(self):
		"""
		Only researchers may be added to the study.
		Thus, adding a participant to a study should fail because the foreign key won't match.
		"""

		self.assert_fail_sql("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._participant_1.get_username()
		), "ForeignKeyViolation")

	@isolated_test
	def test_add_researcher_to_study(self):
		"""
		Test adding a researcher to a study.
		"""

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

	@isolated_test
	def test_remove_researcher_from_study(self):
		"""
		Test that removing a researcher from a study does not remove either the study nor the researcher, but only the link.
		"""

		self._cursor.execute("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Delete the link.
		"""

		self._cursor.execute("""
			DELETE FROM
				studies_researchers
			WHERE
				study_id = '%s' AND
				researcher_id = '%s'
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Ensure that the researcher and the study have not been removed.
		"""

		self._cursor.execute("""
			SELECT *
			FROM
				studies
			WHERE
				study_id = '%s';
		""" % self._study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

		self._cursor.execute("""
			SELECT *
			FROM
				researchers
			WHERE
				user_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

	@isolated_test
	def test_add_researcher_to_nonexistent_study(self):
		"""
		Test adding a researcher to a study that does not exist.
		"""

		self.assert_fail_sql("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			"t" + self._study.get_id(), self._researcher.get_username()
		), "ForeignKeyViolation")

	@isolated_test
	def test_cascading_deletion_researcher(self):
		"""
		Test that removing a researcher removes their links, but not the studies.
		"""

		self._cursor.execute("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Delete the researcher.
		"""

		self._cursor.execute("""
			DELETE FROM
				researchers
			WHERE
				user_id = '%s'
		""" % self._researcher.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				researchers
			WHERE
				user_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Ensure that the link no longer exists, but that the study exists.
		"""

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				studies
			WHERE
				study_id = '%s';
		""" % self._study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

	@isolated_test
	def test_cascading_deletion_user(self):
		"""
		Test that removing a user who is a researcher removes their links, but not the studies.
		"""

		self._cursor.execute("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Delete the researcher.
		"""

		self._cursor.execute("""
			DELETE FROM
				users
			WHERE
				user_id = '%s'
		""" % self._researcher.get_username())

		self._cursor.execute("""
			SELECT *
			FROM
				users
			WHERE
				user_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				researchers
			WHERE
				user_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Ensure that the link no longer exists, but that the study exists.
		"""

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				studies
			WHERE
				study_id = '%s';
		""" % self._study.get_id())
		self.assertEqual(self._cursor.rowcount, 1)

	@isolated_test
	def test_cascading_deletion_study(self):
		"""
		Test that removing a study removes their links, but not the researchers.
		"""

		self._cursor.execute("""
			INSERT INTO
				studies_researchers(study_id, researcher_id)
			VALUES
				('%s', '%s')
		""" % (
			self._study.get_id(), self._researcher.get_username()
		))

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)

		"""
		Delete the study.
		"""

		self._cursor.execute("""
			DELETE FROM
				studies
			WHERE
				study_id = '%s'
		""" % self._study.get_id())

		self._cursor.execute("""
			SELECT *
			FROM
				studies
			WHERE
				study_id = '%s';
		""" % self._study.get_id())
		self.assertEqual(self._cursor.rowcount, 0)

		"""
		Ensure that the link no longer exists, but that the study exists.
		"""

		self._cursor.execute("""
			SELECT *
			FROM
				studies_researchers
			WHERE
				researcher_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 0)

		self._cursor.execute("""
			SELECT *
			FROM
				researchers
			WHERE
				user_id = '%s';
		""" % self._researcher.get_username())
		self.assertEqual(self._cursor.rowcount, 1)
