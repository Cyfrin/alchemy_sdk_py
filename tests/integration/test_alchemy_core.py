from tests.test_data.chainlink_data import (
    CHAINLINK_CODE,
    CHAINLINK_ADDRESS,
    CHAINLINK_CREATOR,
)
from alchemy_sdk_py.utils import bytes32_to_text

# Just some testing data...
PATRICK_ALPHA_C = "0x874437B5a42aA6E6419eC2447C9e36c278c46532"
VITALIK = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
GAS = "0x76c0"
GAS_PRICE = "0x9184e72a000"
VALUE = 0
DATA = "0x3b3b57debf074faa138b72c65adbdcfb329847e4f2c04bde7f7dd7fcad5a52d2f395a558"
TAG = "latest"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

TX_HASH = "0x1ad11558e5bdfb59aae212849ceebcc90670e28e75143c4b5726ce9f3b619358"


def test_call(alchemy_with_key):
    response = alchemy_with_key.call(
        PATRICK_ALPHA_C,
        VITALIK,
        GAS,
        GAS_PRICE,
        VALUE,
        DATA,
    )
    assert response == "0x"


def test_estimate_gas(alchemy_with_key):
    response = alchemy_with_key.estimate_gas(
        PATRICK_ALPHA_C,
        VITALIK,
        GAS,
        GAS_PRICE,
        VALUE,
        DATA,
    )
    assert response == "0x5448"


# def test_find_contract_deployer(alchemy_with_key):
#     response = alchemy_with_key.find_contract_deployer(CHAINLINK)
#     assert response == CHAINLINK_CREATOR


def test_get_balance(alchemy_with_key):
    response = alchemy_with_key.get_balance(PATRICK_ALPHA_C, TAG)
    # Only true if Patrick's ass ain't broke lol
    assert response > 0


def test_get_code(alchemy_with_key):
    response = alchemy_with_key.get_code(CHAINLINK_ADDRESS, TAG)
    assert response == CHAINLINK_CODE


def test_get_transaction_count(alchemy_with_key):
    response = alchemy_with_key.get_transaction_count(PATRICK_ALPHA_C, TAG)
    assert response > 0


def test_get_storage_at(alchemy_with_key):
    # Arrange
    expected_response_string = "Wrapped Ether"

    # Act
    response = alchemy_with_key.get_storage_at(WETH_ADDRESS, 0, TAG)
    decoded_string = bytes32_to_text(response)
    assert decoded_string == expected_response_string


def test_get_block_transaction_count_by_hash(alchemy_with_key):
    # Arrange
    expected = 305
    # Act
    response = alchemy_with_key.get_block_transaction_count_by_hash(TX_HASH)
    # Assert
    assert response == expected


def test_get_block_transaction_count_by_number(alchemy_with_key):
    # Arrange
    number = 16235426
    expected = 305
    # Act
    response = alchemy_with_key.get_block_transaction_count_by_number(number)
    # Assert
    assert response == expected


def test_get_uncle_count_by_blockhash(alchemy_with_key):
    # Arrange
    expected = 0
    response = alchemy_with_key.get_uncle_count_by_blockhash(TX_HASH)
    assert expected == response


# def test_get_block(alchemy_with_key):
#     response = alchemy_with_key.get_block(0)
#     breakpoint()
