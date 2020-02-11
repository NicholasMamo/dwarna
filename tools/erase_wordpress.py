#!/usr/bin/env python3

"""
A function to go through the WordPress data file and erase a list of research partners.
"""

import argparse
import os
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
