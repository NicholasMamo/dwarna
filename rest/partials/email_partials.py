"""
The email partials contain components of an email.
"""

import os
import sys

path = sys.path[0]
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

from config.routes import base_url
