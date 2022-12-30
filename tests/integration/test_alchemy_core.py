from tests.test_data import (
    CHAINLINK_ADDRESS,
    CHAINLINK_CREATOR,
    VITALIK,
    PATRICK_ALPHA_C,
    ENS,
    ETH_BLOCKS,
    PATRICK_ALPHA_C_TOKEN_ID_ENS,
)


def test_set_api_key(alchemy, mock_env_missing):
    # Arrange / Act
    alchemy.set_api_key("Hello")
    # Assert
    assert alchemy.api_key == "Hello"


def test_get_current_block_number(alchemy_with_key):
    # Arrange / Act
    current_block = alchemy_with_key.get_current_block_number()
    # Assert
    assert current_block > 0


def test_get_asset_transfers_page_key(alchemy_with_key):
    # Arrange
    start_block = 0
    end_block = 16271807
    address = "0x165Ff6730D449Af03B4eE1E48122227a3328A1fc"

    # Act
    _, page_key = alchemy_with_key.get_asset_transfers(
        from_address=address, from_block=start_block, to_block=end_block
    )

    # Assert
    assert page_key is not None


def test_get_asset_transfers_page_key_is_none(alchemy_with_key):
    # Arrange
    start_block = 16271807
    end_block = 16271807
    address = "0x165Ff6730D449Af03B4eE1E48122227a3328A1fc"

    # Act
    _, page_key = alchemy_with_key.get_asset_transfers(
        from_address=address, from_block=start_block, to_block=end_block
    )

    # Assert
    assert page_key is None


def test_get_asset_transfers_all(alchemy_with_key):
    # Arrange
    start_block = 0
    end_block = 16291530
    to_address = "0xa5D0084A766203b463b3164DFc49D91509C12daB"
    category = ["erc20"]
    expected_transfers_number = 14185

    # Act
    transfers, _ = alchemy_with_key.get_asset_transfers(
        to_address=to_address,
        from_block=start_block,
        to_block=end_block,
        get_all_flag=True,
        category=category,
    )

    # Assert
    assert len(transfers) == expected_transfers_number


def test_get_transaction_receipts(alchemy_with_key):
    # Arrange
    block_number = 16292979
    expected_from = "0x7944e84d18803f926743fa56fb7a9bb9ba5f5f24"
    # Act
    transaction_receipts = alchemy_with_key.get_transaction_receipts(block_number)
    # Assert
    assert transaction_receipts[0]["from"] == expected_from
    assert len(transaction_receipts) == 132


def test_find_contract_deployer(alchemy_with_key):
    deployer_address, block_number = alchemy_with_key.find_contract_deployer(
        CHAINLINK_ADDRESS
    )
    expected_block_number = 4281611
    assert deployer_address.lower() == CHAINLINK_CREATOR.lower()
    assert block_number == expected_block_number


def test_get_max_priority_fee_per_gas(alchemy_with_key):
    response = alchemy_with_key.get_max_priority_fee_per_gas()
    assert response > 0


def test_get_fee_history(alchemy_with_key):
    current_block = int(alchemy_with_key.get_current_block_number())
    response = alchemy_with_key.get_fee_history(1, current_block)
    assert len(response["baseFeePerGas"]) > 0


def test_fee_data(alchemy_with_key):
    fee_data = alchemy_with_key.get_fee_data()
    assert fee_data["max_fee_per_gas"] > 0
    assert fee_data["max_priority_fee_per_gas"] > 0
    assert fee_data["gas_price"] > 0


def test_get_token_balances_with_address_and_contract_list(alchemy_with_key):
    contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    response = alchemy_with_key.get_token_balances(VITALIK, [contract])
    assert len(response["tokenBalances"]) == 1


def test_get_token_balances_with_type(alchemy_with_key):
    response = alchemy_with_key.get_token_balances(VITALIK, "erc20")
    assert len(response["tokenBalances"]) > 0


def test_get_token_balances_with_page_key(alchemy_with_key):
    setup_response = alchemy_with_key.get_token_balances(VITALIK, "erc20")
    page_key = setup_response["pageKey"]
    response = alchemy_with_key.get_token_balances(VITALIK, "erc20", page_key)
    assert len(response["tokenBalances"]) > 0


def test_get_token_metadata(alchemy_with_key):
    response = alchemy_with_key.get_token_metadata(CHAINLINK_ADDRESS)
    assert response["name"] == "Chainlink"
    assert response["symbol"] == "LINK"


def test_send(alchemy_with_key):
    hash = "0x7ac79af930a26f05ef3ae4b3f9e38cb7323696232aea00e3d3e04394ab1c7234"
    response = alchemy_with_key.send("eth_getTransactionByHash", [hash])
    assert response["from"].lower() == PATRICK_ALPHA_C.lower()


def test_get_nfts(alchemy_with_key):
    response = alchemy_with_key.get_nfts_for_owner(PATRICK_ALPHA_C)
    assert response["totalCount"] > 0


def test_get_owners_for_token(alchemy_with_key):
    response = alchemy_with_key.get_owners_for_token(
        ENS,
        PATRICK_ALPHA_C_TOKEN_ID_ENS,
    )
    assert response["owners"][0].lower() == PATRICK_ALPHA_C.lower()


def test_get_owners_for_nft(alchemy_with_key):
    response = alchemy_with_key.get_owners_for_nft(
        ENS,
        PATRICK_ALPHA_C_TOKEN_ID_ENS,
    )
    assert response["owners"][0].lower() == PATRICK_ALPHA_C.lower()


# I don't think spam filter is working
# def test_get_nfts_spam_check(alchemy_with_key):
#     with_spam = alchemy_with_key.get_nfts(PATRICK_ALPHA_C)
#     no_spam = alchemy_with_key.get_nfts(
#         PATRICK_ALPHA_C, exclude_filters=["SPAM", "AIRDROPS"]
#     )
#     assert with_spam["totalCount"] != no_spam["totalCount"]


def test_get_owners_for_collection(alchemy_with_key):
    current_block_number = alchemy_with_key.get_current_block_number()
    response = alchemy_with_key.get_owners_for_collection(
        ETH_BLOCKS, False, current_block_number
    )
    assert len(response["ownerAddresses"]) > 0


def test_get_owners_for_contract(alchemy_with_key):
    current_block_number = alchemy_with_key.get_current_block_number()
    response = alchemy_with_key.get_owners_for_contract(
        ETH_BLOCKS, False, current_block_number
    )
    assert len(response["ownerAddresses"]) > 0


def test_is_holder_of_collection(alchemy_with_key):
    response = alchemy_with_key.is_holder_of_collection(PATRICK_ALPHA_C, ETH_BLOCKS)
    # Unless I buy one...
    assert response["isHolderOfCollection"] is False


def test_get_contracts_for_owner(alchemy_with_key):
    response = alchemy_with_key.get_contracts_for_owner(PATRICK_ALPHA_C)
    assert len(response["contracts"]) > 0


def test_get_nft_metadata(alchemy_with_key):
    response = alchemy_with_key.get_nft_metadata(ENS, PATRICK_ALPHA_C_TOKEN_ID_ENS)
    assert response["title"].lower() == "patrickalphac.eth"


def test_get_contract_metadata(alchemy_with_key):
    response = alchemy_with_key.get_contract_metadata(ENS)
    assert (
        response["contractMetadata"]["openSea"]["collectionName"]
        == "ENS: Ethereum Name Service"
    )


def test_get_nfts_for_contract(alchemy_with_key):
    response = alchemy_with_key.get_nfts_for_contract(ENS, limit=5)
    assert len(response["nfts"]) == 5


def test_get_nfts_for_collection(alchemy_with_key):
    response = alchemy_with_key.get_nfts_for_collection(ENS, limit=5)
    assert len(response["nfts"]) == 5


def test_get_spam_contracts(alchemy_with_key):
    response = alchemy_with_key.get_spam_contracts()
    assert len(response) > 0


def test_is_spam_contract(alchemy_with_key):
    response = alchemy_with_key.is_spam_contract(ENS)
    assert response is False


def test_refresh_contract(alchemy_with_key):
    response = alchemy_with_key.refresh_contract(ENS)
    assert "reingestionState" in response


def test_get_floor_price(alchemy_with_key):
    response = alchemy_with_key.get_floor_price(ENS)
    assert "openSea" in response
    assert "floorPrice" in response["openSea"]


# Something going wrong here, idk
# def test_compute_rarity(alchemy_with_key):
#     response = alchemy_with_key.compute_rarity(ENS, PATRICK_ALPHA_C_TOKEN_ID_ENS)
#     assert "rarity" in response


def test_verify_nft_ownership(alchemy_with_key):
    response = alchemy_with_key.verify_nft_ownership(PATRICK_ALPHA_C, ENS)
    # find ENS key ignoring caps and case
    assert response[ENS.lower()] == True


def test_alchemy_get_transaction(alchemy_with_key):
    response = alchemy_with_key.get_transaction(
        "0x7ac79af930a26f05ef3ae4b3f9e38cb7323696232aea00e3d3e04394ab1c7234"
    )
    assert response["from"].lower() == PATRICK_ALPHA_C.lower()
