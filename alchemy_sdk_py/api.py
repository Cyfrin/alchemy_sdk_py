import os
from typing import Tuple
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


def get_asset_transfers(
    from_address: str, from_block: int, to_block: int, max_count=1000, page_key=None
) -> Tuple[list, str]:
    """
    params:
        from_address: Address to look for transactions from
        block_start: INT
        block_end: INT
    returns: [list, str]
        A Tuple, index 0 is the list of transfers, index 1 is the page key or None
    """
    from_block = str(hex(from_block))
    to_block = str(hex(to_block))
    address = from_address.lower()
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": from_block,
                "toBlock": to_block,
                "fromAddress": address,
                "category": ["external", "internal", "erc20", "erc721", "specialnft"],
                "excludeZeroValue": False,
                "maxCount": hex(max_count),
            }
        ],
    }
    if page_key:
        payload["params"][0]["pageKey"] = page_key
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    json_response = response.json()
    result = json_response["result"]
    transfers = result["transfers"]
    if "pageKey" in result:
        return transfers, result["pageKey"]
    return transfers, None


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
    json_respnse = response.json()
    result = json_respnse["result"]
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
