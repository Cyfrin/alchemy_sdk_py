import os
from typing import Optional, Union
from alchemy_sdk_py.utils import HexIntStringNumber, is_hash
from .errors import NO_API_KEY_ERROR
from .networks import Network
import requests
from dotenv import load_dotenv

load_dotenv()

HEADERS = {"accept": "application/json", "content-type": "application/json"}
POSSIBLE_BLOCK_TAGS = ["latest", "earliest", "pending", "safe", "finalized"]


class EVM_Node:
    def __init__(
        self,
        api_key: Optional[str] = None,
        key: Optional[str] = None,
        network: Optional[Network] = "eth_mainnet",
        retries: Optional[int] = 0,
        proxy: Optional[dict] = None,
        url: Optional[str] = None,
    ):
        """A python class to interact with the Alchemy API. This class is used to interact with the EVM JSON-RPC API.
        We see most of the typical EVM JSON-RPC endpoints here. For more information on the EVM JSON-RPC API, see
        https://ethereum.org/en/developers/docs/apis/json-rpc/

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
        self.url_network_name = self.network.name.replace("_", "-")
        self.base_url_without_key = f"https://{self.url_network_name}.g.alchemy.com/v2/"
        self.base_url = (
            f"{self.base_url_without_key}{self.api_key}" if url is None else url
        )
        self.retries = retries
        self.proxy = proxy or {}
        self.call_id = 0

    @property
    def key(self) -> str:
        """
        returns:
            API key
        """
        return self.api_key

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
            "id": self.call_id,
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
            "id": self.call_id,
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

    def get_current_block_number(self) -> int:
        """Returns the current block number
        params:
            None
        returns:
            the current max block (INT)
        """
        payload = {"id": self.call_id, "jsonrpc": "2.0", "method": "eth_blockNumber"}
        json_response = self._handle_api_call(payload)
        result = int(json_response.get("result"), 16)
        return result

    def block_number(self) -> int:
        return self.get_current_block_number()

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
            "id": self.call_id,
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
            "id": self.call_id,
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
            "id": self.call_id,
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
            "id": self.call_id,
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
            "id": self.call_id,
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
        tag_hex = HexIntStringNumber(tag).hex if tag not in POSSIBLE_BLOCK_TAGS else tag
        payload = {
            "id": self.call_id,
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
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getUncleCountByBlockHash",
            "params": [block_hash],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_uncle_count_by_block_number(self, tag: Union[int, str]) -> int:
        """Returns the number of uncles in a block from a block matching the given block number.

        Args:
            tag (Union[int, str]): QUANTITY|TAG - integer of a block number, or the string "earliest", "latest" or "pending", as in the default block parameter.
            ie: "latest" or "0xe8"

        Returns:
            int: Number of uncles in a block from a block matching the given block number.
        """
        tag_hex = HexIntStringNumber(tag).hex if tag not in POSSIBLE_BLOCK_TAGS else tag
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getUncleCountByBlockNumber",
            "params": [tag_hex],
        }
        json_response = self._handle_api_call(payload)
        return int(json_response.get("result"), 16)

    def get_block_by_hash(
        self, block_hash: str, full_transaction_objects: bool = False
    ) -> dict:
        """Returns information about a block by hash.

        Args:
            block_hash (str): DATA, 32 Bytes - hash of a block
            full_transaction_objects (bool, optional): If true it returns the full transaction objects, if false only the hashes of the transactions. Defaults to False.

        Returns:
            dict: Block data
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getBlockByHash",
            "params": [block_hash, full_transaction_objects],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result", {})

    def get_block_by_number(
        self, tag: Union[int, str], full_transaction_objects: Optional[bool] = False
    ) -> dict:
        """Returns information about a block by block number.

        Args:
            tag (Union[int, str]): QUANTITY|TAG - integer of a block number, or the string "earliest", "latest" or "pending", as in the default block parameter.
            ie: "latest" or "0xe8"
            full_transaction_objects (bool, optional): If true it returns the full transaction objects, if false only the hashes of the transactions. Defaults to False.

        Returns:
            dict: Block data
        """
        tag_hex = HexIntStringNumber(tag).hex if tag not in POSSIBLE_BLOCK_TAGS else tag
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [tag_hex, full_transaction_objects],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result", {})

    def get_current_block(self) -> dict:
        """
        returns:
            current block data
        """
        current_block: int = self.get_current_block_number()
        return self.get_block_by_number(current_block)

    def get_transaction_by_hash(self, transaction_hash: str) -> dict:
        """Returns the information about a transaction requested by transaction hash.

        Args:
            transaction_hash (str): DATA, 32 Bytes - hash of a transaction

        Returns:
            dict: Transaction data
        """
        if not isinstance(transaction_hash, str):
            raise TypeError("transaction_hash must be a string")
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [transaction_hash],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result", {})

    def get_transaction_by_block_hash_and_index(
        self, block_hash: str, index: int
    ) -> dict:
        """Returns information about a transaction by block hash and transaction index position.

        Args:
            block_hash (str): DATA, 32 Bytes - hash of a block
            index (int): QUANTITY - integer of the transaction index position

        Returns:
            dict: Transaction data
        """
        if not isinstance(block_hash, str):
            raise TypeError("block_hash must be a string")
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByBlockHashAndIndex",
            "params": [block_hash, HexIntStringNumber(index).hex],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result", {})

    def get_transaction_by_block_number_and_index(
        self, tag: Union[int, str], index: int
    ) -> dict:
        """Returns information about a transaction by block number and transaction index position.

        Args:
            tag (Union[int, str]): QUANTITY|TAG - integer of a block number, or the string "earliest", "latest" or "pending", as in the default block parameter.
            ie: "latest" or "0xe8"
            index (int): QUANTITY - integer of the transaction index position

        Returns:
            dict: Transaction data
        """
        tag_hex = HexIntStringNumber(tag).hex if tag not in POSSIBLE_BLOCK_TAGS else tag
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByBlockNumberAndIndex",
            "params": [tag_hex, HexIntStringNumber(index).hex],
        }
        json_response = self._handle_api_call(payload)
        return json_response.get("result", {})

    def get_transaction_receipt(self, transaction_hash: str) -> dict:
        """
        params:
            transaction_hash: transaction hash to search for
        returns:
            transaction receipt data
        """
        if not isinstance(transaction_hash, str):
            raise TypeError("transaction_hash must be a string")
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [transaction_hash],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    def get_uncle_by_block_hash_and_index(self, block_hash: str, index: int) -> dict:
        """
        params:
            block_hash: block hash to search for
            index: index of the uncle to search for
        returns:
            uncle data
        """
        if not isinstance(block_hash, str):
            raise TypeError("block_hash must be a string")
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getUncleByBlockHashAndIndex",
            "params": [block_hash, HexIntStringNumber(index).hex],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    # make a function for eth_getUncleByBlockNumberAndIndex

    def get_uncle_by_block_number_and_index(
        self, tag: Union[int, str], index: int
    ) -> dict:
        """
        params:
            tag: block number to search for
            index: index of the uncle to search for
        returns:
            uncle data
        """
        tag_hex = HexIntStringNumber(tag).hex if tag not in POSSIBLE_BLOCK_TAGS else tag
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getUncleByBlockNumberAndIndex",
            "params": [tag_hex, HexIntStringNumber(index).hex],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    def client_version(self) -> str:
        """
        params:
            None
        returns:
            client version string
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    def sha(self, data: str) -> str:
        """Convert data to sha3 hash
        Args:
            data (str): data to convert
        Returns:
            str: sha3 hash
        """
        if not isinstance(data, str):
            raise TypeError("data must be a string")
        if not data.startswith("0x"):
            data = hex(int.from_bytes(data.encode(), "big"))
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "web3_sha3",
            "params": [data],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    def net_version(self) -> str:
        """
        params:
            None
        returns:
            network version string
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "net_version",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    def net_listening(self) -> bool:
        """
        params:
            None
        returns:
            True if client is actively listening for network connections
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "net_listening",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", False)
        return result

    # Currently not implemented by Alchemy
    # def net_peer_count(self) -> int:
    #     """
    #     params:
    #         None
    #     returns:
    #         number of peers currently connected to the client
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "net_peerCount",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", "")
    #     return int(result, 16)

    def protocol_version(self) -> str:
        """
        params:
            None
        returns:
            ethereum protocol version string
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_protocolVersion",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    def syncing(self) -> Union[bool, dict]:
        """
        params:
            None
        returns:
            False if not syncing, otherwise a dictionary with sync status info
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_syncing",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", False)
        return result

    # Not supported by Alchemy
    # def coinbase(self) -> str:
    #     """
    #     params:
    #         None
    #     returns:
    #         coinbase address
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "eth_coinbase",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", "")
    #     return result

    # Not supported by Alchemy
    # def mining(self) -> bool:
    #     """
    #     params:
    #         None
    #     returns:
    #         True if client is actively mining new blocks
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "eth_mining",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", False)
    #     return result

    # Not supported by Alchemy
    # def hashrate(self) -> str:
    #     """
    #     params:
    #         None
    #     returns:
    #         number of hashes per second that the node is mining with
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "eth_hashrate",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", "")
    #     return result

    def gas_price(self) -> int:
        """
        params:
            None
        returns:
            current gas price in wei
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "0")
        return HexIntStringNumber(result).int

    def get_gas_price(self) -> int:
        """
        params:
            None
        returns:
            current gas price in wei
        """
        return self.gas_price()

    # Unsupported by Alchemy
    # def get_compilers(self) -> list[str]:
    #     """
    #     params:
    #         None
    #     returns:
    #         a list of available compilers in the client
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "eth_getCompilers",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", [])
    #     return result

    # Unsupported by Alchemy
    # def get_work(self) -> list[str]:
    #     """
    #     params:
    #         None
    #     returns:
    #         a list of values required by the proof-of-work consensus algorithm
    #     """
    #     payload = {
    #         "id": self.call_id,
    #         "jsonrpc": "2.0",
    #         "method": "eth_getWork",
    #         "params": [],
    #     }
    #     json_response = self._handle_api_call(payload)
    #     result = json_response.get("result", [])
    #     return result

    def get_logs(
        self,
        contract_address: str,
        topics: Union[list[str], str],
        from_block: Union[str, int, None] = 0,
        to_block: Union[str, int, None] = "latest",
    ) -> list:
        return self.get_events(contract_address, topics, from_block, to_block)

    def get_events(
        self,
        contract_address: str,
        topics: Union[list[str], str],
        from_block: Union[str, int, None] = 0,
        to_block: Union[str, int, None] = "latest",
    ) -> list:
        """
        params:
            contract_address: address of the contract
            topics: list of topics to filter by (event signatures)
            from_block: block number, or one of "earliest", "latest", "pending"
            to_block: block number, or one of "earliest", "latest", "pending"

        returns: A dictionary, result[block] = block_date
        """
        topics = topics if isinstance(topics, list) else [topics]
        from_block_hex = from_block
        to_block_hex = to_block
        if from_block not in POSSIBLE_BLOCK_TAGS:
            from_block_hex = HexIntStringNumber(from_block).hex
            to_block_hex = HexIntStringNumber(to_block).hex
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [
                {
                    "address": contract_address,
                    "fromBlock": from_block_hex,
                    "toBlock": to_block_hex,
                    "topics": topics,
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
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [data],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "")
        return result

    ############################################################
    ################ Internal/Raw Methods ######################
    ############################################################

    def _handle_api_call(
        self,
        payload: dict,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
        """Handles making the API calls to Alchemy... It should be refactored, it's gross

        params:
            payload: the payload to send to the API
            endpoint: the endpoint to send the payload to
            url: the url to send the payload to
            http_method: the http method to use
        returns: a dictionary of the response
        """
        url = self.base_url if url is None else url
        headers = HEADERS
        if endpoint is not None:
            headers["Alchemy-Python-Sdk-Method"] = endpoint
        response = requests.post(url, json=payload, headers=headers, proxies=self.proxy)
        if response.status_code != 200:
            retries_here = 0
            while retries_here < self.retries and response.status_code != 200:
                retries_here = retries_here + 1
                response = requests.post(
                    url, json=payload, headers=headers, proxies=self.proxy
                )
            if response.status_code != 200:
                raise ConnectionError(
                    f'Status {response.status_code} when querying "{self.base_url_without_key}<REDACTED_API_KEY>/" with payload {payload}:\n >>> Response with Error: {response.text}'
                )
        json_response = response.json()
        if (
            json_response.get("result", None) is None
            or json_response.get("error", None) is not None
        ):
            raise ConnectionError(
                f'Status {response.status_code} when querying "{self.base_url_without_key}<REDACTED_API_KEY>/" with payload {payload}:\n >>> Response with Error: {response.text}'
            )
        self.call_id = self.call_id + 1
        return json_response
