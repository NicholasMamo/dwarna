"""
An abstract, generic representation of a smart contract.
"""

from abc import ABC, abstractmethod

import ast
import json
import re

class Contract(ABC):
	"""
	The contract class stores the ABI and bytecode associated with the contract.
	"""

	def load_abi(f):
		"""
		Load the ABI from the given file.

		:param f: The file object that contains the ABI.
		:type f: file

		:return: The ABI as a list.
		:rtype: list
		"""

		s = ""

		for line in f:
			"""
			Go through each line and add its contents to the string representation.
			"""

			s = s + line.strip()

		"""
		Capitalize the boolean flags, otherwise the parser fails.
		"""
		false_pattern = re.compile("\": false,")
		true_pattern = re.compile("\": true,")
		s = false_pattern.sub("\": False,", s)
		s = true_pattern.sub("\": True,", s)

		return ast.literal_eval(s)

	def load_bytecode(f):
		"""
		Load the bytecode from the given file.

		:param f: The file object that contains the bytecode.
		:type f: file

		:return: The bytecode as an associative array.
		:rtype: dict
		"""

		return json.loads(''.join(f.readlines()).strip())["object"]
