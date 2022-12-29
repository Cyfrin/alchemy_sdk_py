from datetime import datetime
from typing import Optional, Tuple, Union
import os
from .errors import NO_API_KEY_ERROR
from .networks import Network
import requests
from dotenv import load_dotenv
from .utils import HexIntStringNumber, is_hex_int

load_dotenv()

HEADERS = {"accept": "application/json", "content-type": "application/json"}


class Alchemy:
    def __init__(
        self,
        api_key: Optional[str] = None,
        key: Optional[str] = None,
        network: Optional[Network] = "eth_mainnet",
        retries: Optional[int] = 0,
        proxy: Optional[dict] = None,
        url: Optional[str] = None,
    ):
        """A python class to interact with the Alchemy API

        Args:
            api_key (Optional[str], optional): The API key of your alchemy instance. Defaults to None.
            key (Optional[str], optional): Another way to pass an api key.
            network (Optional[str], optional): The network you want to work on. Defaults to None.
            retries (Optional[int], optional): The number of times to retry a request. Defaults to 0.
            proxy (Optional[dict], optional): A proxy to use for requests. Defaults to None.
            url (Optional[str], optional): A custom url to use for requests. Defaults to None.

        Raises:
            ValueError: If you give it a bad network or API key it'll error
        """
        if key:
            api_key = key
        if api_key is None:
            api_key = os.getenv("ALCHEMY_API_KEY")
        if not api_key or not isinstance(api_key, str):
            raise ValueError(NO_API_KEY_ERROR)
        self.api_key = api_key
        self.network = Network(network)
        url_network_name = self.network.name.replace("_", "-")
        self.base_url_without_key = f"https://{url_network_name}.g.alchemy.com/v2/"
        self.base_url = (
            f"{self.base_url_without_key}{self.api_key}" if url is None else url
        )
        self.retries = retries
        self.proxy = proxy or {}

    ############################################################
    ################ ETH JSON-RPC Methods ######################
    ############################################################

    def call(
        self,
        from_address: str,
        to_address: str,
        gas: Union[str, int],
        gas_price: Union[str, int],
        value: Union[int, str, None] = "0",
        data: Optional[str] = "0x0",
        tag: Union[str, dict, None] = "latest",
    ) -> str:
        """Call a smart contract function

        Args:
            from_address (str): The address to call from
            to_address (str): The address to call to
            gas (int): The gas to use
            gas_price (int): The gas price to use
            value (int): The value to send
            data (str): The data to send
            tag (Union[str, dict, None]): The tag to use. "latest", "earlist", "pending", or a block number like:
            {"blockHash": "0x<some-hash>"}

        Returns:
            str: The result of the call
        """
        tag = tag.lower() if isinstance(tag, str) else tag
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [
                {
                    "from": from_address,
                    "to": to_address,
                    "gas": HexIntStringNumber(gas).hex,
                    "gasPrice": HexIntStringNumber(gas_price).hex,
                    "value": HexIntStringNumber(value).hex,
                    "data": data,
                },
                tag,
            ],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result")

    def estimate_gas(
        self,
        from_address: str,
        to_address: str,
        gas: Union[str, int],
        gas_price: Union[str, int],
        value: Union[int, str, None] = "0",
        data: Optional[str] = "0x0",
        tag: Union[str, dict, None] = "latest",
    ) -> str:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_estimateGas",
            "params": [
                {
                    "from": from_address,
                    "to": to_address,
                    "gas": HexIntStringNumber(gas).hex,
                    "gasPrice": HexIntStringNumber(gas_price).hex,
                    "value": HexIntStringNumber(value).hex,
                    "data": data,
                },
                tag.lower(),
            ],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result")

    # def find_contract_deployer(self, contract_address: str) -> str:
    #     """Find the address that deployed a contract

    #     Args:
    #         contract_address (str): The contract address

    #     Returns:
    #         str: The address that deployed the contract
    #     """
    #     if not isinstance(contract_address, str):
    #         raise ValueError("contract_address must be a string")
    #     current_block: int = self.get_current_block()

    #     # payload = {
    #     #     "contractAddress": contract_address,
    #     # }
    #     # json_response = self._handle_api_call(payload, endpoint="findContractDeployer")
    #     # return json_response.get("result")

    def get_current_block(self) -> int:
        """
        params:
            None
        returns:
            the current max block (INT)
        """
        payload = {"id": 1, "jsonrpc": "2.0", "method": "eth_blockNumber"}
        json_response = self._handle_api_call(payload)
        result = int(json_response.get("result"), 16)
        return result

    def _get_all_asset_transfers(
        self,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        from_block: Union[int, str, None] = 0,
        to_block: Union[int, str, None] = None,
        contract_addresses: Optional[list] = None,
        category: Optional[list[str]] = [
            "external",
            "internal",
            "erc20",
            "erc721",
            "specialnft",
        ],
    ) -> list:
        """
        params:
            from_address: Address to look for transactions from
            from_block: int (1), hex ("0x1"), or str "1"
            to_block: int (1), hex ("0x1"), or str "1"
            contract_addresses: List of contract addresses to filter by
            category: List of categories to filter by
        returns:
            a list of asset transfers
        """
        total_transfers = []
        page_key = None
        first_run = True
        while page_key is not None or first_run:
            first_run = False
            transfers, page_key = self.get_asset_transfers(
                from_address=from_address,
                to_address=to_address,
                from_block=from_block,
                to_block=to_block,
                page_key=page_key,
                contract_addresses=contract_addresses,
                category=category,
            )
            total_transfers.extend(transfers)
        return total_transfers, None

    def get_asset_transfers(
        self,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        from_block: Union[int, str, None] = 0,
        to_block: Union[int, str, None] = None,
        max_count: Union[int, str, None] = 1000,
        page_key: Optional[str] = None,
        contract_addresses: Optional[list] = None,
        category: Optional[list[str]] = [
            "external",
            "internal",
            "erc20",
            "erc721",
            "specialnft",
        ],
        get_all_flag: Optional[bool] = False,
    ) -> Tuple[list, str]:
        """
        params:
            from_address: Address to look for transactions from
            from_block: int (1), hex ("0x1"), or str "1"
            to_block: int (1), hex ("0x1"), or str "1"
            max_count: Max number of transactions to return
            page_key: A unique key to get the next page of results
            contract_addresses: A list of contract addresses to filter by (for erc20, erc721, specialnft)
            category: A list of categories to filter by (external, internal, erc20, erc721, specialnft)

        returns: [list, str]
            A Tuple, index 0 is the list of transfers, index 1 is the page key or None
        """
        if to_block is None:
            to_block = self.get_current_block()
        from_block_hex = HexIntStringNumber(from_block).hex
        to_block_hex = HexIntStringNumber(to_block).hex
        from_address = from_address.lower() if from_address else None
        to_address = to_address.lower() if to_address else None
        if get_all_flag:
            return self._get_all_asset_transfers(
                from_address=from_address,
                to_address=to_address,
                from_block=from_block_hex,
                to_block=to_block_hex,
                contract_addresses=contract_addresses,
                category=category,
            )
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": from_block_hex,
                    "toBlock": to_block_hex,
                    "category": category,
                    "excludeZeroValue": False,
                    "maxCount": HexIntStringNumber(max_count).hex,
                }
            ],
        }
        if page_key:
            payload["params"][0]["pageKey"] = page_key
        if contract_addresses:
            payload["params"][0]["contractAddresses"] = contract_addresses
        if from_address:
            payload["params"][0]["fromAddress"] = from_address
        if to_address:
            payload["params"][0]["toAddress"] = to_address

        json_response = self._handle_api_call(payload)
        result = json_response.get("result")
        transfers = result.get("transfers", -1)
        if transfers == -1:
            raise ValueError(f"No transfers found. API response: {json_response}")
        if "pageKey" in result:
            return transfers, result["pageKey"]
        return transfers, None

    def get_balance(
        self,
        address: str,
        tag: Union[str, dict, None] = "latest",
    ) -> int:
        """
        params:
            address: address to get balance of
            tag:  "latest", "earliest", "pending", or an dict with a block number
            ie: {"blockNumber": "0x1"}

        returns:
            balance of address (int)
        """
        tag = tag.lower() if isinstance(tag, str) else tag
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, tag],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_code(self, address: str, tag: Union[str, dict, None] = "latest") -> str:
        """Returns code at a given address.

        Args:
            address (str): DATA, 20 Bytes - address
            tag (Union[str, dict, None], optional): tag:  "latest", "earliest", "pending", or an dict with a block number
            ie: {"blockNumber": "0x1"}. Defaults to "latest".

        Returns:
            str: Code at given address
        """
        tag = tag.lower() if isinstance(tag, str) else tag
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getCode",
            "params": [address, tag],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result")

    def get_transaction_count(
        self, address: str, tag: Union[str, dict, None] = "latest"
    ) -> int:
        """Returns the number of transactions sent from an address.

        Args:
            address (str): DATA, 20 Bytes - address
            tag (Union[str, dict, None], optional): tag:  "latest", "earliest", "pending", or an dict with a block number
            ie: {"blockNumber": "0x1"}. Defaults to "latest".

        Returns:
            int: Number of transactions sent from an address
        """
        tag = tag.lower() if isinstance(tag, str) else tag
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [address, tag],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_storage_at(
        self,
        address: str,
        storage_position: Union[int, str],
        tag: Union[str, dict, None] = "latest",
    ) -> str:
        """Returns the value from a storage position at a given address.

        Args:
            address (str): DATA, 20 Bytes - address
            storage_position (Union[int, str]): QUANTITY - integer of the position in the storage.
            tag (Union[str, dict, None], optional): tag:  "latest", "earliest", "pending", or an dict with a block number
            ie: {"blockNumber": "0x1"}. Defaults to "latest".

        Returns:
            str: The value at this storage position.
        """
        tag = tag.lower() if isinstance(tag, str) else tag
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getStorageAt",
            "params": [address, HexIntStringNumber(storage_position).hex, tag],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result")

    def get_block_transaction_count_by_hash(self, block_hash: str) -> int:
        """Returns the number of transactions in a block from a block matching the given block hash.

        Args:
            block_hash (str): DATA, 32 Bytes - hash of a block

        Returns:
            int: Number of transactions in a block from a block matching the given block hash.
        """
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getBlockTransactionCountByHash",
            "params": [block_hash],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_block_transaction_count_by_number(self, tag: Union[int, str]) -> int:
        """Returns the number of transactions in a block from a block matching the given block number.

        Args:
            tag (Union[int, str]): QUANTITY|TAG - integer of a block number, or the string "earliest", "latest" or "pending", as in the default block parameter.
            ie: "latest" or "0xe8"

        Returns:
            int: Number of transactions in a block from a block matching the given block number.
        """
        tag_hex = (
            HexIntStringNumber(tag).hex
            if tag not in ["latest", "earliest", "pending"]
            else tag
        )
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getBlockTransactionCountByNumber",
            "params": [tag_hex],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_uncle_count_by_blockhash(self, block_hash: str) -> int:
        """Returns the number of uncles in a block from a block matching the given block hash.

        Args:
            block_hash (str): DATA, 32 Bytes - hash of a block

        Returns:
            int: Number of uncles in a block from a block matching the given block hash.
        """
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getUncleCountByBlockHash",
            "params": [block_hash],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    # def get_block(self, block_number_or_hash: Union[str, int]) -> dict:
    #     """
    #     params:
    #         block_number: block number to get (can be int, string, or hash)
    #     returns:
    #         block data
    #     """
    #     if isinstance(block_number_or_hash, str):
    #         if is_hex_int(block_number_or_hash):
    #             block_number_or_hash = HexIntStringNumber(block_number_or_hash).hex
    #     else:
    #         block_number_or_hash = HexIntStringNumber(block_number_or_hash).hex
    #     payload = {
    #         "params": [block_number_or_hash],
    #     }
    #     json_response = self._handle_api_call(payload, endpoint="getBlock")
    #     result = json_response.get("result", {})
    #     return result

    def get_transaction_receipt(self, transaction_hash: str) -> dict:
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
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    def get_events(
        self,
        contract_address: str,
        event_signature: str,
        from_block: Union[str, int, None],
        to_block: Union[str, int, None],
    ) -> dict:
        """
        params:
            contract_address: LIST off addresses for which to search for events
            event_signature: signature of the event to search for (TOPIC 0)
            from_block: INT
            to_block: INT
        returns: A dictionary, result[block] = block_date
        """
        from_block_hex = HexIntStringNumber(from_block).hex
        to_block_hex = HexIntStringNumber(to_block).hex
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [
                {
                    "address": contract_address,
                    "fromBlock": from_block_hex,
                    "toBlock": to_block_hex,
                    "topics": [event_signature],
                }
            ],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    def send_raw_transactions(self, data: str) -> str:
        """
        params:
            data: raw transaction data
        returns: transaction hash

        Note: I ain't bothering to test this.
        """
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [data],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    def get_block_by_number():
        pass

    def get_datetime_of_blocks(
        self, blocks=None, from_block=None, to_block=None
    ) -> dict:
        """
        params:
                from_block as an INT
                to_block as an INT
        returns:
                A dictionary, result[block] = block_date
        """
        blocks = list(range(from_block, to_block)) if blocks is None else blocks
        result = {}
        for block in blocks:
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block), False],
            }
            json_response = self._handle_api_call(payload)
            result_raw = json_response.get("result", None)
            block = int(result_raw["number"], 16)
            block_date = datetime.fromtimestamp(int(result_raw["timestamp"], 16))
            result[block] = block_date
        return result

    def set_api_key(self, api_key: str):
        """
        params:
            key: API key
        returns:
            None
        """
        if not isinstance(api_key, str):
            raise ValueError(NO_API_KEY_ERROR)
        self.api_key = api_key

    def set_network(self, network: str):
        """
        params:
            network: Network to use
        returns:
            None
        """
        self.network = Network(network)
        url_network_name = self.network.name.replace("_", "-")
        self.base_url_without_key = f"https://{url_network_name}.g.alchemy.com/v2/"
        self.base_url = f"{self.base_url_without_key}{self.api_key}"

    def set_settings(self, key: Optional[str] = None, network: Optional[str] = None):
        """
        params:
            key: API key
            network: Network to use
        returns:
            None
        """
        if key:
            self.set_api_key(key)
        if network:
            self.set_network(network)

    @property
    def key(self) -> str:
        """
        returns:
            API key
        """
        return self.api_key

    def _handle_api_call(self, payload: dict, endpoint: Optional[str] = None) -> dict:
        url = self.base_url if endpoint is None else f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=payload, headers=HEADERS, proxies=self.proxy)
        if response.status_code != 200:
            retries_here = 0
            while retries_here < self.retries and response.status_code != 200:
                retries_here = retries_here + 1
                response = requests.post(
                    url, json=payload, headers=HEADERS, proxies=self.proxy
                )
            if response.status_code != 200:
                raise ConnectionError(
                    f'Status {response.status_code} when querying "{self.base_url_without_key}<REDACTED_API_KEY>/{endpoint}" with payload {payload}:\n >>> Response with Error: {response.text}'
                )
        json_response = response.json()
        if (
            json_response.get("result", None) is None
            or json_response.get("error", None) is not None
        ):
            raise ConnectionError(
                f'Status {response.status_code} when querying "{self.base_url_without_key}<REDACTED_API_KEY>/{endpoint}" with payload {payload}:\n >>> Response with Error: {response.text}'
            )
        return json_response
