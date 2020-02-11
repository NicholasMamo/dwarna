#!/usr/bin/env python3

"""
A function to go through a list of PostgreSQL files and erase a list of research partners.
"""

import argparse
import os
import sys

COLUMNS = {
	"participant_identities.csv": "participant_id",
	"participant_subscriptions.csv": "participant_id",
	"participants.csv": "user_id",
}
"""
:var COLUMNS: The columns where to look for pseudonyms in each file.
:vartype COLUMNS: dict
"""

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

def get_column_index(column, header):
	"""
	Get the index of the given column in the header line.

	:param column: The column name to look for.
	:type column: str
	:param header: The header line.
	:type header: str

	:return: The index of the column name in the header line.
	:rtype: int
	"""

	column_names = header.split(',')
	return column_names.index(column)

def erase(path, pseudonym):
	"""
	Erase the research partner having the given pseudonym from the backup in the given path.

	:param path: The path to the backup directory.
	:type path: str
	:param pseudonym: The pseudonym of the research partner to remove.
	:type pseudonym: str

	:raises OSError: If there is no PostgreSQL backup in the given path.
	"""

	dir = os.path.join(path, 'postgresql')
	if not os.path.isdir(dir):
		raise OSError("No PostgreSQL backup found")

	for file, column in COLUMNS.items():
		file = os.path.join(dir, file)
		with open(file, "r") as fin, open(f"{file}.tmp", "w") as fout:
			header = fin.readline()
			index = get_column_index(column, header)
			fout.write(header)
			for line in fin:
				data = line.split(',')
				if data[index] != pseudonym:
					fout.write(line)

		"""
		Remove the original file and replace it with the new one.
		"""
		os.remove(file)
		os.rename(f"{file}.tmp", file)

if __name__ == "__main__":
	args = setup_args()
	path = args.path[0]

	for pseudonym in args.erase:
		erase(path, pseudonym)
