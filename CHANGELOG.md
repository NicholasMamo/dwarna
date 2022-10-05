# CHANGELOG

## V2.0.0 - Ethereum

In this release, the blockchain used to store consent changes was changed from Hyperledger to Ethereum.

In order for this change to happen the following was done:
1. A private POW Ethereum network was set up
2. The smart contracts in <b>rest/biobank/handlers/blockchain/api/ethereum/contracts</b> were deployed
3. The REST backend server was changed by changing the blockchain handler class to EthereumAPI rather than HyperledgerAPI
4. The EthereumAPI blockchain handler class connects to the private Ethereum network created in Step 1 by changing the RPC endpoint of a blockchain node in <b>rest/biobank/handlers/blockchain/api/ethereum/ethereum.py</b>

```python
w3= web3.Web3(web3.HTTPProvider('http://127.0.0.1:8543'))
```
5. Changed the database table <b>participant_identities</b> to <b>participant_identities_eth</b> in order to follow the new credentials structure
6. Changed the flow of some calls made from the biobank plugin to the rest server since in this version, there is no need for the authentication step with Hyperledger. With this version, the plugin can communicate directly with the REST server and then private keys are used to authenticate users.

