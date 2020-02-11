#!/usr/bin/env python3

"""
A function to go through the WordPress data file and erase a list of research partners.
"""

import argparse
import os
import re
import sys

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:
		- -e --erase	A list of research partners to erase.
		- -p --path		The path to the backup directory.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Erase research partners from PostgreSQL backups.")
	parser.add_argument("-p", "--path", nargs=1, required=True,
						help="<Required> The path to the backup directory.")
	parser.add_argument("-e", "--erase", nargs="+", required=True,
						help="<Required> A list of research partners to erase.")
	args = parser.parse_args()
	return args

def get_table_structure(path, table):
	"""
	Extract the table structure from the given file.

	:param path: The path to the SQL file.
	:type path: str
	:param table: The table whose structure to extract.
	:type table: str

	:return: A list of lines making up the table structure.
	:rtype: list
	"""

	lines = []

	found = False # whether the table has been found
	with open(path, 'r') as f:
		for line in f:
			"""
			Table structures always start the same, so look for the SQL function.
			"""
			if line.startswith(f"CREATE TABLE `{table}`"):
				found = True

			"""
			Stop reading when the first break after the table structure is found.
			"""
			if found and line.startswith('--'):
				break

			"""
			If the table structure has been found, add it to the list of lines.
			"""
			if found:
				lines.append(line)

	return lines

def get_table_data(path, table):
	"""
	Extract the table data from the given file.

	:param path: The path to the SQL file.
	:type path: str
	:param table: The table whose data to extract.
	:type table: str

	:return: The data tuple inserted into the table.
	:rtype: list of list of str
	"""

	with open(path, 'r') as f:
		for line in f:
			"""
			Table structures always start the same and occupy one line.
			"""
			if line.startswith(f"INSERT INTO `{table}`"):
				data_pattern = re.compile("(\\(.+?\\))")
				data = data_pattern.findall(line)
				data = [ tuple.replace("'", '') for tuple in data]
				data = [ tuple.replace("(", '') for tuple in data]
				data = [ tuple.replace(")", '') for tuple in data]
				data = [ tuple.split(',') for tuple in data]
				return data

	return [ ]

def get_column_index(lines, column):
	"""
	Get the index of the given column in the given table structure.

	:param lines: The table structure lines where to look for the column.
	:type lines: str
	:param column: The column to look for.
	:type column: str

	:return: The index of the column name in the table structure.
	:rtype: int
	"""

	i = 0

	line_pattern = re.compile('\\s+`')
	column_pattern = re.compile('`(.+?)`')
	for line in lines:
		"""
		Check whether the line starts with a few spaces and a column name.
		"""
		if line_pattern.match(line) and line_pattern.match(line).start() == 0:
			name = column_pattern.findall(line)[0]
			if name == column:
				return i

			i += 1
	return False

def get_user_id(path, pseudonym):
	"""
	Get the user ID for the user having the given pseudonym.
	The function looks in the `wp_users` table.

	:param path: The path to the SQL file.
	:type path: str
	:param pseudonym: The pseudonym of the research partner to remove.
	:type pseudonym: str

	:return: The user ID for the user having the given pseudonym.
			 If the user ID is not found, -1 is returned.
	:rtype: int
	"""

	structure = get_table_structure(path, 'wp_users')
	data = get_table_data(path, 'wp_users')
	id_index = get_column_index(structure, 'ID')
	user_login_index = get_column_index(structure, 'user_login')

	for tuple in data:
		if tuple[user_login_index] == pseudonym:
			return tuple[id_index]

	return -1

def erase(path, pseudonym):
	"""
	Erase the research partner having the given pseudonym from the backup in the given path.

	:param path: The path to the backup directory.
	:type path: str
	:param pseudonym: The pseudonym of the research partner to remove.
	:type pseudonym: str

	:raises OSError: If there is no PostgreSQL backup in the given path.
	"""

	dir = os.path.join(path, 'wordpress')
	if not os.path.isdir(dir):
		raise OSError("No WordPress backup found")

if __name__ == "__main__":
	args = setup_args()
	path = args.path[0]

	for pseudonym in args.erase:
		erase(path, pseudonym)
