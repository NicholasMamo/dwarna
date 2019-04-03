"""
A study contract, based on a normal smart contract.
"""

import os
import sys

from web3.auto import w3

import web3

from .contract import Contract

class Study(Contract):
	"""
	The study class is based on a normal contract.
	However, it implements the ABI and bytecode.

	:cvar abi: The contract's Application Binary Interface (ABI).
	:vartype abi: list
	:cvar bytecode: The contract's bytecode.
	:vartype bytecode: dict
	"""

	@staticmethod
	def deploy():
		"""
		Deploy a new contract.

		:return: The transaction hash, which can be awaited until the contract is mined.
		:rtype: str
		"""

		study = w3.eth.contract(abi=Study.abi, bytecode=Study.bytecode)
		return study.constructor().transact()

	@staticmethod
	def load_study(address):
		"""
		Load the study at the given address.

		:param address: The address where the study is located.
		:type address: str

		:return: The study at the given address.
		:rtype: :class:`web3.utils.datatypes.Contract`
		"""

		address = w3.toChecksumAddress(address)
		study = w3.eth.contract(abi=Study.abi, bytecode=Study.bytecode, address=address)
		return study

	@staticmethod
	def load(abi_file, bytecode_file):
		"""
		Load the smart contract's data from the two given files.
		The ABI and bytecode are saved into class variables, thus being shared among instances.

		:param abi_file: The file object that contains the contract's ABI.
		:type abi_file: file
		:param bytecode_file: The file object that contains the contract's bytecode.
		:type bytecode_file: file
		"""

		Study.abi = Contract.load_abi(abi_file)
		Study.bytecode = Contract.load_bytecode(bytecode_file)

"""
Load the ABI and bytecode immediately.
"""
with open(os.path.join(os.path.dirname(__file__), "data", "abi.json"), "r") as abi_file, open(os.path.join(os.path.dirname(__file__), "data", "bytecode.json"), "r") as byte_file :
	Study.load(abi_file, byte_file)
