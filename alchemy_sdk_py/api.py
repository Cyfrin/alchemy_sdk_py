import os
import requests
import json
from decimal import Decimal
from datetime import datetime

API_KEY = os.getenv("ALCHEMY_API_KEY")
BASE_URL = f"https://eth-mainnet.g.alchemy.com/v2/{API_KEY}"
HEADERS = {"accept": "application/json", "content-type": "application/json"}


def set_api_key(key: str):
    """
    params:
        key: API key
    returns:
        None
    """
    os.environ["ALCHEMY_API_KEY"] = key


def get_current_block() -> int:
    """
    params:
        None
    returns:
        the current max block (INT)
    """
    payload = {"id": 1, "jsonrpc": "2.0", "method": "eth_blockNumber"}
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response = json.loads(response.text)
    result = int(response["result"], 16)
    return result


def get_asset_transfers(node_address: str, block_start: int, block_end: int) -> list:
    """
    params:
        node_address: wallet address associated with the OCR node
        block_start: INT
        block_end: INT
    returns: A dictionary, internal/external asset transfers for the address
    """
    from_block = str(hex(block_start))
    to_block = str(hex(block_end))
    address = node_address.lower()
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": from_block,
                "toBlock": to_block,
                "fromAddress": address,
                "category": ["external", "internal"],
                "excludeZeroValue": False,
            }
        ],
    }
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response = json.loads(response.text)
    result = response["result"]
    transfers = result["transfers"]
    return transfers


def get_transaction_receipt(transaction_hash: str):
    """
    params:
        transaction_hash: transaction hash to search for
    returns:
        transaction receipt data
    """
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [transaction_hash],
    }
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response = json.loads(response.text)
    result = response["result"]
    return result


def get_events(contract_address, event_signature, block_start, block_end) -> dict:
    """
    params:
        contract_address: LIST off addresses for which to search for events
        event_signature: signature of the event to search for (TOPIC 0)
        block_start: INT
        block_end: INT
    returns: A dictionary, result[block] = block_date
    """
    from_block = str(hex(block_start))
    to_block = str(hex(block_end))
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [
            {
                "address": contract_address,
                "fromBlock": from_block,
                "toBlock": to_block,
                "topics": [event_signature],
            }
        ],
    }
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response = json.loads(response.text)
    result = response.get("result")
    return result


def get_block_datetime(blocks=None, block_start=None, block_end=None) -> dict:
    """
    params:
            block_start as an INT
            block_end as an INT
    returns:
            A dictionary, result[block] = block_date
    """
    blocks = list(range(block_start, block_end)) if blocks is None else blocks
    result = {}
    for block in blocks:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [hex(block), False],
        }
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        result_raw = json.loads(response.text)["result"]
        block = int(result_raw["number"], 16)
        block_date = datetime.fromtimestamp(int(result_raw["timestamp"], 16))
        result[block] = block_date
    return result
