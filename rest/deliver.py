#!/usr/bin/env python3

"""
A script to deliver emails that have not been sent yet.
"""

import argparse
import requests

from config import oauth

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:
		- -p --port		The port on which to serve the REST API, defaults to 7225.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Serve the REST API which controls the dynamic consent functionality.")
	parser.add_argument("-p", "--port", nargs="+", type=str, default=7225, help="<Optional> The port on which to serve the REST API, defaults to 7225.", required=False)
	args = parser.parse_args()
	return args

def main(port=None):
	"""
	Deliver the next email.

	:param port: The port on which the REST API is listening.
	:type port: int
	"""

	pass

if __name__ == "__main__":
	args = setup_args()
	port = args.port
	main(port)
