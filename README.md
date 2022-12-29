# alchemy_sdk_py (Pre-Alpha)
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

### Useage 

```python
from alchemy_sdk_py import Alchemy

alchemy = Alchemy()

current_block = alchemy.get_current_block()
print(current_block)
```

# Currently not implemented

- [ ] `batchRequests`
- [ ] `web sockets`
- [ ] `Notify API`
- [ ] `Async support`