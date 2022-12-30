# alchemy_sdk_py (Beta)
An SDK to use the [Alchemy API](https://www.alchemy.com/)


<br/>
<p align="center">
<a href="https://alchemy.com/?a=673c802981" target="_blank">
<img src="./img/logo.png" width="225" alt="Alchemy logo">
</a>
</p>
<br/>

- [alchemy\_sdk\_py (Pre-Alpha)](#alchemy_sdk_py-pre-alpha)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
    - [Get an API Key](#get-an-api-key)
- [Useage](#useage)
  - [Get all ERC20, value, and NFT transfers for an address](#get-all-erc20-value-and-nft-transfers-for-an-address)
  - [Get contract metadata for any NFT](#get-contract-metadata-for-any-nft)
- [What's here and what's not](#whats-here-and-whats-not)
  - [What this currently has](#what-this-currently-has)
  - [Currently not implemented](#currently-not-implemented)


# Getting Started

## Requirements 

- [Python](https://www.python.org/downloads/) 3.7 or higher
    - You'll know you've done it right if you can run `python3 --version` in your terminal and see something like `Python 3.10.6`

## Installation

```bash
pip3 install alchemy_sdk_py
```

## Quickstart

### Get an API Key
After [installing](#installation), you'll need to sign up for an API key and set it as an `ALCHEMY_API_KEY` environment variable. You can place them in a `.env` file if you like *just please don't push the `.env` file to GitHub*.

`.env`
```bash
ALCHEMY_API_KEY="asdfasfsfasf
```

If you're unfamiliar with environment variables, you can use the API to set the key directly using the SDK - please don't do this in production code. 

```python
from alchemy_sdk_py import Alchemy

alchemy = Alchemy(api_key="asdfasfsfasf", network="eth_mainnet")
```
If you have your environment variable set, and you want to use eth mainnet, you can just do this: 

```python
from alchemy_sdk_py import Alchemy
alchemy = Alchemy()
```

You can also set the network ID using the chainId, or hex, and even update it later. 
```python
# For Goerli ETH
alchemy = Alchemy(network=5)
# For Polygon ("0x89" is hex for 137)
alchemy.set_network("0x89")
```

# Useage 

```python
from alchemy_sdk_py import Alchemy

alchemy = Alchemy()

current_block_number = alchemy.get_current_block_number()
print(current_block_number)
# prints the current block number
```

With web3.py

```python
from alchemy_sdk_py import Alchemy
from web3 import Web3

alchemy = Alchemy()

w3 = Web3(Web3.HTTPProvider(alchemy.base_url))
```

## Get all ERC20, value, and NFT transfers for an address

The following code will get you every transfer in and out of a single wallet address. 

```python
from alchemy_sdk_py import Alchemy
alchemy = Alchemy()

address = "YOUR_ADDRESS_HERE"

transfers, page_key = alchemy_with_key.get_asset_transfers(from_address=address)
print(transfers)
# prints every transfer in or out that's ever happened on the address
```

## Get contract metadata for any NFT

```python
ENS = "0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85"
contract_metadata = alchemy_with_key.get_contract_metadata(ENS)

print(contract_metadata["contractMetadata"]["openSea"]["collectionName"])
# prints "ENS: Ethereum Name Service"
```

# What's here and what's not

## What this currently has

Just about everything in the [Alchemy SDK](https://docs.alchemy.com/reference/alchemy-sdk-quickstart) section of the docs. 

## Currently not implemented

- [ ] `batchRequests`
- [ ] `web sockets`
- [ ] `Notify API` & `filters` ie `eth_newFilter`
- [ ] `Async support`
- [ ] ENS Support for addresses
- [ ] Double check the NFT, Transact, and Token docs for function
- [ ] Trace API
- [ ] Debug API
