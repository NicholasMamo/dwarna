"""
Stop mining the blockchain.
"""

from web3.auto import w3

w3.miner.stop()
