# alchemy_sdk_py
An SDK to use the [Alchemy API](https://www.alchemy.com/)


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
After [installing](#installation), you'll need to sign up for an API key and set it as an `ALCHEMY_API_KEY` environment variable. 

If you're unfamiliar with environment variables, you can use the API to set the key directly using the SDK - please don't do this in production code. 

```python
import alchemy_sdk_py

alchemy_sdk_py.set_api_key("YOUR_API_KEY")
```

This will make the key availible for the duration of your script. 

### Useage 

```python
import alchemy_sdk_py as alchemy

current_block = alchemy.get_current_block()
print(current_block)
```
