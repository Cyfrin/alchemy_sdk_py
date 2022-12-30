from datetime import datetime
from typing import Optional, Tuple, Union
from .errors import NO_API_KEY_ERROR
from .networks import Network
from .utils import HexIntStringNumber, ETH_NULL_VALUE, is_hash, is_hex_int
from .evm_node import POSSIBLE_BLOCK_TAGS, EVM_Node, HEADERS
import requests
import time

NFT_FILTERS = ["SPAM", "AIRDROPS"]


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

    @property
    def nft_url(self) -> str:
        """The url for the NFT API"""
        return f"https://{self.url_network_name}.g.alchemy.com/nft/v2/{self.api_key}"

    @property
    def ws_url(self) -> str:
        """The url for the websocket"""
        return f"wss://{self.url_network_name}.g.alchemy.com/v2/{self.api_key}"

    @property
    def webhook_url(self) -> str:
        """The url for the webhook"""
        return f"https://dashboard.alchemy.com/api"

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
            to_block = self.get_current_block_number()
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
        current_block: int = self.get_current_block_number()
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
    ################ NFT Methods ###############################
    ############################################################

    def get_nfts_for_owner(
        self,
        owner: str,
        page_key: Optional[str] = None,
        page_size: Optional[int] = 100,
        contract_addresses: Optional[list[str]] = None,
        omit_metadata: Optional[bool] = False,
        token_uri_timeout_in_ms: Union[int, None] = None,
        filters: Optional[list[str]] = None,
    ) -> dict:
        """Gets all NFTs currently owned by a given address.

        params:
            owner: Address of the owner to get NFTs for
            page_key: Optional page key to get the next page of results
            page_size: Optional page size to get the next page of results
            contract_addresses: Optional list of contract addresses to get NFTs for
            omit_metadata: Optional boolean to omit metadata
            token_uri_timeout_in_ms: Optional timeout in ms for token URI requests
            filters: Optional list of strings from "SPAM" and "AIRDROPS"
        returns:
            Dictionary of NFTs
        """
        return self.get_nfts(
            owner,
            page_key,
            page_size,
            contract_addresses,
            with_metadata=not omit_metadata,
            token_uri_timeout_in_ms=token_uri_timeout_in_ms,
            exclude_filters=filters,
        )

    def get_nfts(
        self,
        owner: str,
        page_key: Optional[str] = None,
        page_size: Optional[int] = 100,
        contract_addresses: Optional[list[str]] = None,
        with_metadata: Optional[bool] = False,
        token_uri_timeout_in_ms: Union[int, None] = None,
        exclude_filters: Optional[list[str]] = None,
        include_filters: Optional[list[str]] = None,
        order_by: Optional[str] = None,
    ) -> dict:
        """Gets all NFTs currently owned by a given address.

        params:
            owner: Address of the owner to get NFTs for
            page_key: Optional page key to get the next page of results
            page_size: Optional page size to get the next page of results
            contract_addresses: Optional list of contract addresses to get NFTs for
            with_metadata: Optional boolean to include metadata
            token_uri_timeout_in_ms: Optional timeout in ms for token URI requests
            exclude_filters: Optional list of strings from "SPAM" and "AIRDROPS"
            include_filters: Optional list of strings from "SPAM" and "AIRDROPS"
            order_by: Optional string to order by "transferTime" or None

        returns:
            Dictionary of NFTs
        """
        params = {"owner": owner}
        if page_key:
            params["pageKey"] = page_key
        if page_size:
            params["pageSize"] = page_size
        if contract_addresses:
            params["contractAddresses"] = contract_addresses
        if with_metadata:
            params["withMetadata"] = with_metadata
        if token_uri_timeout_in_ms:
            params["tokenUriTimeoutInMs"] = token_uri_timeout_in_ms
        if exclude_filters:
            params["excludeFilters"] = exclude_filters
        if include_filters:
            params["includeFilters"] = include_filters
        if order_by:
            params["orderBy"] = order_by
        json_response = self._handle_get_call(
            "getNFTs",
            params=params,
            endpoint="getNFTsForOwner",
            url=self.nft_url,
        )
        return json_response

    def get_owners_for_token(
        self, contract_address: str, token_id: Union[str, int]
    ) -> dict:
        """Get the owner(s) for a token.

        Args:
            contract_address (str): Contract address of the token
            token_id (Union[str, int, None]): Token ID of the token

        Returns:
            dict: Dictionary of owners
        """
        params = {"contractAddress": contract_address}
        params["tokenId"] = HexIntStringNumber(token_id).int
        json_response = self._handle_get_call(
            "getOwnersForToken",
            params=params,
            endpoint="getOwnersForToken",
            url=self.nft_url,
        )
        return json_response

    def get_owners_for_nft(
        self, contract_address: str, token_id: Union[str, int]
    ) -> dict:
        """Get the owner(s) for a token.

        Args:
            contract_address (str): Contract address of the token
            token_id (Union[str, int, None]): Token ID of the token

        Returns:
            dict: Dictionary of owners
        """
        return self.get_owners_for_token(contract_address, token_id)

    def get_owners_for_collection(
        self,
        contract_address: str,
        with_token_balances: bool,
        block: Union[str, int],
        page_key: Optional[str] = None,
    ) -> dict:
        """Gets all owners for a given NFT contract.

        Returns:
            dict: Dictionary of owners
        """
        params = {
            "contractAddress": contract_address,
            "withTokenBalances": with_token_balances or False,
            "block": HexIntStringNumber(block).str,
        }
        if page_key:
            params["pageKey"] = page_key
        json_response = self._handle_get_call(
            "getOwnersForCollection",
            params=params,
            endpoint="getOwnersForCollection",
            url=self.nft_url,
        )
        return json_response

    def is_holder_of_collection(self, wallet: str, contract_address: str) -> dict:
        """Checks if a wallet is a holder of a collection.

        Args:
            wallet (str): Wallet address to check
            contract_address (str): Contract address of the collection

        Returns:
            dict: Dictionary of owners
        """
        params = {
            "wallet": wallet,
            "contractAddress": contract_address,
        }
        json_response = self._handle_get_call(
            "isHolderOfCollection",
            params=params,
            endpoint="isHolderOfCollection",
            url=self.nft_url,
        )
        return json_response

    def get_contracts_for_owner(
        self,
        owner: str,
        page_key: Optional[str] = None,
        page_size: Optional[int] = 100,
        include_filters: Optional[list[str]] = None,
        exclude_filters: Optional[list[str]] = None,
        order_by: Optional[str] = None,
    ) -> dict:
        """Gets all contracts for a given owner.

        Args:
            owner (str): Owner address to check
            page_key (Optional[str], optional): Page key to get the next page of results. Defaults to None.
            page_size (Optional[int], optional): Page size to get the next page of results. Defaults to 100.
            include_filters (Optional[list[str]], optional): Optional list of strings from "SPAM" and "AIRDROPS". Defaults to None.
            exclude_filters (Optional[list[str]], optional): Optional list of strings from "SPAM" and "AIRDROPS". Defaults to None.
            order_by (Optional[str], optional): Optional string to order by "transferTime" or None. Defaults to None.

        Returns:
            dict: Dictionary of contracts
        """
        params = {
            "owner": owner,
        }
        if page_key:
            params["pageKey"] = page_key
        if page_size:
            params["pageSize"] = page_size
        if include_filters:
            params["includeFilters"] = include_filters
        if exclude_filters:
            params["excludeFilters"] = exclude_filters
        if order_by:
            params["orderBy"] = order_by
        json_response = self._handle_get_call(
            "getContractsForOwner",
            params=params,
            endpoint="getContractsForOwner",
            url=self.nft_url,
        )
        return json_response

    def get_nft_metadata(
        self,
        contract_address: str,
        token_id: Union[str, int],
        token_type: str = "ERC721",
        token_uri_timeout_in_ms: int = 0,
        refresh_cache: bool = False,
    ) -> dict:
        """Gets the metadata for a given NFT.

        Args:
            contract_address (str): Contract address of the NFT
            token_id (Union[str, int]): Token ID of the NFT
            token_type (str, optional): Token type of the NFT. Defaults to "ERC721", can also be "ERC1155".
            token_uri_timeout_in_ms (int, optional): Timeout in ms for the token URI. Defaults to 0.
            refresh_cache (bool, optional): Refresh the cache. Defaults to False.

        Returns:
            dict: Dictionary of metadata
        """
        params = {
            "contractAddress": contract_address,
            "tokenId": HexIntStringNumber(token_id).int,
        }
        if token_type:
            params["tokenType"] = token_type
        if token_uri_timeout_in_ms:
            params["tokenUriTimeoutInMs"] = token_uri_timeout_in_ms
        if refresh_cache:
            params["refreshCache"] = refresh_cache
        json_response = self._handle_get_call(
            "getNFTMetadata",
            params=params,
            endpoint="getNFTMetadata",
            url=self.nft_url,
        )
        return json_response

    def get_contract_metadata(self, contract_address: str) -> dict:
        """Queries NFT high-level collection/contract level information.

        Args:
            contract_address (str): Contract address of the NFT

        Returns:
            dict: Dictionary of metadata
        """
        params = {
            "contractAddress": contract_address,
        }
        json_response = self._handle_get_call(
            "getContractMetadata",
            params=params,
            endpoint="getContractMetadata",
            url=self.nft_url,
        )
        return json_response

    def get_nfts_for_contract(
        self,
        contract_address: str,
        omit_metadata: bool = False,
        start_token: Union[str, int, None] = None,
        limit: Optional[int] = 100,
        token_uri_timeout_in_ms: Optional[int] = None,
    ) -> dict:
        """Gets all NFTs for a given NFT contract.

        Args:
            contract_address (str): Contract address of the NFT
            omit_metadata (bool, optional): Omit metadata. Defaults to False.
            startToken (Union[str, int, None], optional): Start token. Defaults to None.
            limit (Optional[int], optional): Limit. Defaults to 100.
            token_uri_timeout_in_ms (Optional[int], optional): Token URI timeout in ms. Defaults to None.

        Returns:
            dict: Dictionary of NFTs
        """
        return self.get_nfts_for_collection(
            contract_address,
            with_metadata=not omit_metadata,
            start_token=start_token,
            limit=limit,
            token_uri_timeout_in_ms=token_uri_timeout_in_ms,
        )

    def get_nfts_for_collection(
        self,
        contract_address: str,
        with_metadata: Optional[bool] = False,
        start_token: Optional[int] = None,
        limit: Optional[int] = 100,
        token_uri_timeout_in_ms: Optional[int] = None,
    ) -> dict:
        """Gets all NFTs for a given NFT contract.

        Args:
            contract_address (str): Contract address of the NFT
            with_metadata (Optional[bool], optional): With metadata. Defaults to False.
            start_token (Optional[int], optional): Start token. Defaults to None.
            limit (Optional[int], optional): Limit. Defaults to 100.
            token_uri_timeout_in_ms (Optional[int], optional): Token URI timeout in ms. Defaults to None.

        Returns:
            dict: Dictionary of NFTs
        """
        params = {
            "contractAddress": contract_address,
        }
        if with_metadata:
            params["withMetadata"] = with_metadata
        if start_token:
            params["startToken"] = start_token
        if limit:
            params["limit"] = limit
        if token_uri_timeout_in_ms:
            params["tokenUriTimeoutInMs"] = token_uri_timeout_in_ms
        json_response = self._handle_get_call(
            "getNFTsForCollection",
            params=params,
            endpoint="getNFTsForCollection",
            url=self.nft_url,
        )
        return json_response

    def get_owners_for_contract(
        self,
        contract_address: str,
        with_token_balances: Optional[bool],
        block: Union[str, int],
        page_key: Optional[str] = None,
    ) -> dict:
        """Gets all owners for a given NFT contract.

        Returns:
            dict: Dictionary of owners
        """
        return self.get_owners_for_collection(
            contract_address,
            with_token_balances,
            block,
            page_key=page_key,
        )

    def get_spam_contracts(self) -> dict:
        """Gets all spam contracts.

        Returns:
            dict: Dictionary of spam contracts
        """
        json_response = self._handle_get_call(
            "getSpamContracts",
            endpoint="getSpamContracts",
            url=self.nft_url,
        )
        return json_response

    def is_spam_contract(self, contract_address: str) -> bool:
        """Checks if a contract is a spam contract.

        Returns:
            bool: True if spam contract, False otherwise
        """
        spam_contracts = self.get_spam_contracts()
        return contract_address in spam_contracts

    def reingest_contract(self, contract_address: str) -> dict:
        """Refreshes a contract.

        Returns:
            dict: Dictionary of refreshed contract
        """
        params = {
            "contractAddress": contract_address,
        }
        json_response = self._handle_get_call(
            "reingestContract",
            params=params,
            endpoint="reingestContract",
            url=self.nft_url,
        )
        return json_response

    def refresh_contract(self, contract_address: str) -> dict:
        """Reingests a contract.

        Returns:
            dict: Dictionary of reingested contract
        """
        return self.reingest_contract(contract_address)

    def get_floor_price(self, contract_address) -> dict:
        """Gets floor price for a contract.

        Returns:
            dict: Dictionary of floor price
        """
        params = {
            "contractAddress": contract_address,
        }
        json_response = self._handle_get_call(
            "getFloorPrice",
            params=params,
            endpoint="getFloorPrice",
            url=self.nft_url,
        )
        return json_response

    def compute_rarity(self, contract_address: str, token_id: Union[str, int]) -> dict:
        """Computes rarity for a given token.

        Returns:
            dict: Dictionary of rarity
        """
        params = {
            "contractAddress": contract_address,
            "tokenId": HexIntStringNumber(token_id).hex,
        }
        json_response = self._handle_get_call(
            "computeRarity",
            params=params,
            endpoint="computeRarity",
            url=self.nft_url,
        )
        return json_response

    def verify_nft_ownership(
        self, wallet_address: str, contract_addresses: Union[str, list[str]]
    ) -> dict:
        """Verifies if a wallet owns a given NFT.

        Returns:
            dict: Returns a dict of contract addresses and whether or not the wallet owns the NFT
        """
        if isinstance(contract_addresses, str):
            contract_addresses = [contract_addresses]
        contract_addresses = [contract.lower() for contract in contract_addresses]
        nfts_for_owner = self.get_nfts_for_owner(
            wallet_address, contract_addresses=contract_addresses, omit_metadata=True
        )
        contract_addresses_dict = {contract: False for contract in contract_addresses}
        for nft in nfts_for_owner["ownedNfts"]:
            if nft["contract"]["address"].lower() in contract_addresses_dict:
                contract_addresses_dict[nft["contract"]["address"]] = True
        return contract_addresses_dict

    ############################################################
    ################ Transact Methods ##########################
    ############################################################

    def get_transaction(self, transaction_hash: str) -> dict:
        """Gets a transaction by hash.

        Returns:
            dict: Dictionary of transaction
        """
        return self.get_transaction_by_hash(transaction_hash)

    def send_transaction(self, signed_transaction: str) -> dict:
        """Sends a signed transaction.

        Returns:
            dict: Dictionary of transaction
        """
        return self.send_raw_transaction(signed_transaction)

    def send_private_transaction(
        self,
        method: str = "eth_sendPrivateTransaction",
        tx: str = None,
        max_block_number: Union[int, str] = 999999999,
        fast: bool = False,
    ) -> dict:
        """Sends a private transaction.

        Returns:
            dict: Dictionary of transaction
        """
        params = [
            {
                "tx": tx,
                "maxBlockNumber": HexIntStringNumber(max_block_number).hex,
                "preferences": {"fast": fast},
            }
        ]
        response = self.send(method, params)
        return response

    def cancel_private_transaction(
        self,
        transaction_hash: str = None,
    ) -> dict:
        """Cancels a private transaction.

        Returns:
            dict: Dictionary of transaction
        """
        method = "eth_cancelPrivateTransaction"
        params = [
            {
                "txHash": transaction_hash,
            }
        ]
        response = self.send(method, params)
        return response

    def wait_for_transaction(
        self,
        transaction_hash: str,
        confirmations: Optional[int] = 1,
        timeout: Optional[int] = 60,
    ) -> dict:
        """Waits for a transaction to be confirmed.

        Returns:
            dict: Dictionary of transaction
        """
        receipt = self.get_transaction_receipt(transaction_hash)
        if receipt["confirmations"] >= confirmations:
            return receipt
        # start a loop that will check the number of confirmatoins every 5 seconds
        start_time = time.time()
        while (
            time.time() - start_time < timeout
            and receipt["confirmations"] < confirmations
        ):
            time.sleep(5)
            receipt = self.get_transaction_receipt(transaction_hash)
            if receipt["confirmations"] >= confirmations:
                return receipt
        raise TimeoutError(
            f"Transaction {transaction_hash} did not get {confirmations} confirmations in {timeout} seconds"
        )

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

    ############################################################
    ################ Internal/Raw Methods ######################
    ############################################################

    def _handle_get_call(
        self,
        rest_endpoint: str,
        params: Optional[dict] = None,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
        """Handles a GET call to the Alchemy backend. Sort of shitty. Should be refactored with `_handle_api_call`.

        params:
            rest_endpoint: REST endpoint to call
            params: Optional dictionary of parameters to pass to the endpoint
            endpoint: Optional endpoint to pass to the backend
            url: Optional URL to call
        returns:
            Dictionary of the response
        """
        url = self.base_url if url is None else url
        url = f"{url}/{rest_endpoint}"
        headers = HEADERS
        if endpoint is not None:
            headers["Alchemy-Python-Sdk-Method"] = endpoint
        response = requests.get(url, params=params, headers=headers, proxies=self.proxy)
        if response.status_code != 200:
            retries_here = 0
            while retries_here < self.retries and response.status_code != 200:
                retries_here = retries_here + 1
                response = requests.post(
                    url, params=params, headers=headers, proxies=self.proxy
                )
            if response.status_code != 200:
                raise ConnectionError(
                    f"Status {response.status_code} with params {params}:\n >>> Response with Error: {response.text}"
                )
        json_response = response.json()
        if isinstance(json_response, dict):
            if json_response.get("error", None) is not None:
                raise ConnectionError(
                    f"Status {response.status_code} with params {params}:\n >>> Response with Error: {response.text}"
                )
        self.call_id = self.call_id + 1
        return json_response
