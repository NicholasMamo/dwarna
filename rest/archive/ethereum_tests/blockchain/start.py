"""
Initialize the blockchain and start mining.
"""

from web3.auto import w3

"""
Create a default account.
"""
w3.personal.newAccount("pwd")

w3.miner.start(1)
