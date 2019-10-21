"""
Test the email management functionality in the backend.
"""

import json
import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

import main

from .environment import *

from .test import BiobankTestCase

class EmailManagementTest(BiobankTestCase):
	"""
	Test the backend's email management functionality.
	"""

	pass
