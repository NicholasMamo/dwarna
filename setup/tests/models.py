"""
Database models to facilitate SQL insertion commands.
"""

from abc import ABC, abstractmethod

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

	def __init__(self, name, description, homepage):
		self._name = name
		self._description = description
		self._homepage = homepage

	def set_id(self, id):
		self._id = id

	def get_id(self):
		return self._id

	def get_insertion_string(self):
		return "'%s', '%s', '%s'" % (self._name, self._description, self._homepage)
