from datetime import datetime
from typing import Optional, Tuple, Union
from .errors import NO_API_KEY_ERROR
from .networks import Network
from .utils import HexIntStringNumber, ETH_NULL_VALUE, is_hash
from .evm_node import POSSIBLE_BLOCK_TAGS, EVM_Node


class Alchemy(EVM_Node):
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

            Check the evm_node.py file for more details on these arguments and initialization.

        Raises:
            ValueError: If you give it a bad network or API key it'll error
        """
        super().__init__(
            api_key=api_key,
            key=key,
            network=network,
            retries=retries,
            proxy=proxy,
            url=url,
        )

    ############################################################
    ################ Alchemy SDK Methods ######################
    ############################################################

    def get_transaction_receipts(
        self,
        block_number_or_hash: Union[str, int],
    ) -> list:
        """An enhanced api that gets all transaction receipts for a given block by number or block hash.
        Supported on all networks for Ethereum, Polygon, and Arbitrum.

        params:
            block_number_or_hash: The block number or hash
        returns:
            The transaction receipts for the block
        """
        input = {}
        if is_hash(block_number_or_hash):
            input = {"blockHash": block_number_or_hash}
        else:
            input = {"blockNumber": HexIntStringNumber(block_number_or_hash).hex}
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "alchemy_getTransactionReceipts",
            "params": [input],
        }
        json_response = self._handle_api_call(
            payload, endpoint="getTransactionReceipts"
        )
        result = json_response.get("result", {"receipts": []})
        return result["receipts"]

    def binary_search_first_block(
        self,
        from_block: Union[str, int],
        to_block: Union[str, int],
        contract_address: str,
    ) -> int:
        """
        params:
            from_block: int (1), hex ("0x1"), or str "1"
            to_block: int (1), hex ("0x1"), or str "1"
            contract_address: The address of the contract
        returns:
            The first block where the contract was deployed
        """
        if not isinstance(contract_address, str):
            raise TypeError("contract_address must be a string")
        from_block = HexIntStringNumber(from_block)
        to_block = HexIntStringNumber(to_block)
        if from_block.int >= to_block.int:
            return to_block.int
        mid_block = HexIntStringNumber((from_block.int + to_block.int) // 2)
        code = self.get_code(contract_address, mid_block.hex)
        if code == ETH_NULL_VALUE:
            return self.binary_search_first_block(
                mid_block.int + 1, to_block.int, contract_address
            )
        return self.binary_search_first_block(
            from_block.int, mid_block.int, contract_address
        )

    def find_contract_deployer(self, contract_address: str) -> Tuple[str, int]:
        """
        params:
            contract_address: The address of the contract
        returns:
            The address of the contract deployer
        """
        if not isinstance(contract_address, str):
            raise TypeError("contract_address must be a string")
        current_block_number = self.get_block("latest")["number"]
        code = self.get_code(contract_address, current_block_number)
        if code == ETH_NULL_VALUE:
            raise ValueError("Contract not found")
        first_block = self.binary_search_first_block(
            0, current_block_number, contract_address
        )
        tx_receipts: list = self.get_transaction_receipts(first_block)
        matching_receipt = [
            receipt
            for receipt in tx_receipts
            if str(receipt["contractAddress"]).lower() == contract_address.lower()
        ]
        if len(matching_receipt) == 0:
            raise ValueError("Contract not found")

        return matching_receipt[0]["from"], first_block

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
        NOTE: This will make a LOT of API calls if you're not careful!

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
            get_all_flag: If True, will make multiple API calls to get all results

            NOTE: If get_all_flag is true, you risk making a LOT of API calls!

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
            "id": self.call_id,
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

        json_response = self._handle_api_call(payload, endpoint="getAssetTransfers")
        result = json_response.get("result")
        transfers = result.get("transfers", -1)
        if transfers == -1:
            raise ValueError(f"No transfers found. API response: {json_response}")
        if "pageKey" in result:
            return transfers, result["pageKey"]
        return transfers, None

    def get_block(self, block_number_or_hash_or_tag: Union[str, int]) -> dict:
        """
        params:
            block_number: block number to get (can be int, string, or hash, or tag like "latest", "earliest", "pending")
        returns:
            block data
        """
        if block_number_or_hash_or_tag in POSSIBLE_BLOCK_TAGS:
            return self.get_block_by_number(block_number_or_hash_or_tag)
        if is_hash(block_number_or_hash_or_tag):
            return self.get_block_by_hash(block_number_or_hash_or_tag)
        return self.get_block_by_number(block_number_or_hash_or_tag)

    def get_block_number(self) -> int:
        """
        returns:
            current block number
        """
        current_block: int = self.get_current_block()
        return current_block

    def get_block_with_transactions(
        self, block_hash_number_or_tag: Union[str, int]
    ) -> dict:
        """
        params:
            block_number: block number to get (can be int, string, or hash, or tag like "latest", "earliest", "pending")
        returns:
            block data
        """
        if block_hash_number_or_tag in POSSIBLE_BLOCK_TAGS:
            return self.get_block_by_number(block_hash_number_or_tag, True)
        if is_hash(block_hash_number_or_tag):
            return self.get_block_by_hash(block_hash_number_or_tag, True)
        return self.get_block_by_number(block_hash_number_or_tag, True)

    def fee_data(self) -> dict:
        return self.get_fee_data()

    def get_fee_data(self) -> dict:
        """Returns the recommended fee data to use in a transaction.
        For an EIP-1559 transaction, the maxFeePerGas and maxPriorityFeePerGas should be used.
        For legacy transactions and networks which do not support EIP-1559,
        the gasPrice should be used.

        Returns:
            dict: _description_
        """
        max_fee_per_gas = self.get_max_fee_per_gas()
        max_priority_fee_per_gas = self.get_max_priority_fee_per_gas()
        gas_price = self.get_gas_price()
        return {
            "max_fee_per_gas": max_fee_per_gas,
            "max_priority_fee_per_gas": max_priority_fee_per_gas,
            "gas_price": gas_price,
        }

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
                "id": self.call_id,
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

    def max_priority_fee_per_gas(self) -> int:
        return self.get_max_priority_fee_per_gas()

    def get_max_priority_fee_per_gas(self) -> int:
        """
        params:
            None
        returns:
            current max priority fee per gas in wei
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_maxPriorityFeePerGas",
            "params": [],
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", "0")
        return HexIntStringNumber(result).int

    def get_fee_history(
        self,
        block_count: int,
        newest_block: Union[str, int],
        reward_percentiles: int = None,
    ) -> dict:
        """
        params:
            None
        returns:
            current fee history
        """
        if newest_block in POSSIBLE_BLOCK_TAGS:
            newest_block = self.get_block(newest_block)["number"]
        params = (
            [HexIntStringNumber(block_count).hex, HexIntStringNumber(newest_block).hex]
            if not reward_percentiles
            else [block_count, newest_block, reward_percentiles]
        )
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "eth_feeHistory",
            "params": params,
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    def fee_history(
        self,
        block_count: int,
        newest_block: Union[str, int],
        reward_percentiles: int = None,
    ) -> dict:
        return self.get_fee_history(block_count, newest_block, reward_percentiles)

    def max_fee_per_gas(self) -> int:
        return self.get_max_fee_per_gas()

    def get_max_fee_per_gas(self) -> int:
        base_fee_per_gas = self.get_base_fee_per_gas()
        max_priority_fee_per_gas = self.get_max_priority_fee_per_gas()
        return base_fee_per_gas + max_priority_fee_per_gas

    def get_base_fee_per_gas(self) -> int:
        fee_history = self.fee_history(1, "latest")
        base_fee_per_gas = fee_history["baseFeePerGas"][0]
        return HexIntStringNumber(base_fee_per_gas).int

    def base_fee_per_gas(self) -> int:
        return self.get_base_fee_per_gas()

    def get_token_balances(
        self,
        address: str,
        token_addresses_or_type: Union[list[str], str, None] = None,
        options_or_page_key: Union[dict, str, None] = None,
    ) -> dict:
        """
        params:
            address: Address to get token balances for
            token_addresses: List of token addresses to get balances for, OR the string "DEFAULT_TOKENS"
            or the string "erc20", or none
            options_or_page_key: Optional dictionary of options that contains a pagekey, or a page key
        returns:
            Dictionary of token balances
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenBalances",
        }
        json_response = {}
        if isinstance(token_addresses_or_type, list):
            if len(token_addresses_or_type) > 1500:
                raise ValueError("Too many token addresses")
            if len(token_addresses_or_type) == 0:
                raise ValueError("No token addresses")
            payload["params"] = [address, token_addresses_or_type]
            json_response = self._handle_api_call(payload, endpoint="getTokenBalances")
        else:
            params = [address]
            if not token_addresses_or_type:
                params.append("erc20")
            else:
                params.append(token_addresses_or_type)
            if isinstance(options_or_page_key, str):
                params.append({"pageKey": options_or_page_key})
            else:
                params.append(options_or_page_key or {})
            payload["params"] = params
            json_response = self._handle_api_call(payload, endpoint="getTokenBalances")
        result = json_response.get("result", {})
        return result

    def get_token_metadata(self, token_address: str) -> dict:
        """
        params:
            token_address: Address of the token to get metadata for
        returns:
            Dictionary of token metadata
        """
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [token_address],
        }
        json_response = self._handle_api_call(payload, endpoint="getTokenMetadata")
        result = json_response.get("result", {})
        return result

    def send(self, method: str, parameters: list) -> dict:
        """Allows sending a raw message to the Alchemy backend.

        params:
            method: RPC method to call
            parameters: List of parameters to pass to the method
        returns:
            Dictionary of the response
        """
        if not isinstance(parameters, list):
            parameters = [parameters]
        payload = {
            "id": self.call_id,
            "jsonrpc": "2.0",
            "method": method,
            "params": parameters,
        }
        json_response = self._handle_api_call(payload)
        result = json_response.get("result", {})
        return result

    ############################################################
    ################ Settings Methods ##########################
    ############################################################

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
