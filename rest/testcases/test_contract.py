"""
Test contract loading and instatiation.
"""

from web3.auto import w3

import os
import sys

path = sys.path[0]
path = os.path.join(path, "..")
if path not in sys.path:
	sys.path.insert(1, path)

from blockchain.ethereum.contract import Contract
from blockchain.ethereum.study import Study

address = "0x41E4F1E2537499f7d7Bb321f0a5195A706ec128D"

with open(os.path.join(os.path.dirname(__file__), "..", "blockchain", "ethereum", "data", "abi.json"), "r") as abi_file, open(os.path.join(os.path.dirname(__file__), "..", "blockchain", "ethereum", "data", "bytecode.json"), "r") as byte_file :
	Study.load(abi_file, byte_file)

# w3.eth.defaultAccount = w3.eth.accounts[0]
# w3.personal.unlockAccount(w3.eth.accounts[0], "pwd")
#
# tx_hash = Study.deploy()
# print("Waiting")
# tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=30)
# address = tx_receipt.contractAddress
# print(address, type(address))

study = Study.load_study(address)

participant = w3.toChecksumAddress("0x2c5f0812754e96cba1a0263aa995f2c64e2ab386")

print(study.functions.get_consenting_participants().call())
print(study.functions.has_consented(participant).call())

exit()

tx_hash = study.functions.withdraw_consent().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

print(study.functions.get_consenting_participants().call())
print(study.functions.has_consented().call())

# tx_hash = study.functions.give_consent().transact()
# tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#
# print(study.functions.get_consenting_participants().call())
# print(study.functions.has_consented().call())
