from tests.test_data import (
    CHAINLINK_CODE,
    CHAINLINK_ADDRESS,
    PATRICK_ALPHA_C,
    VITALIK,
    GAS,
    GAS_PRICE,
    VALUE,
    DATA,
    TAG,
    TX_HASH,
    WETH_ADDRESS,
)
from alchemy_sdk_py.utils import bytes32_to_text, HexIntStringNumber


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


def test_get_uncle_count_by_block_number(alchemy_with_key):
    # Arrange
    expected = 0
    response = alchemy_with_key.get_uncle_count_by_block_number(16235426)
    assert expected == response


def test_get_block_by_hash(alchemy_with_key):
    hash = "0x50f4aaf5aa0e7f2be6766c406e542a42bc980b14f85500ee14f4873cb20d411c"
    full_tx = False
    expected_miner = "0x199d5ed7f45f4ee35960cf22eade2076e95b253f"
    response = alchemy_with_key.get_block_by_hash(hash, full_tx)
    assert response["miner"] == expected_miner


def test_get_block_by_number(alchemy_with_key):
    number = 16292589
    full_tx = False
    expected_miner = "0x199d5ed7f45f4ee35960cf22eade2076e95b253f"
    response = alchemy_with_key.get_block_by_number(number, full_tx)
    assert response["miner"] == expected_miner


def test_get_transaction_by_hash(alchemy_with_key):
    hash = "0x7ac79af930a26f05ef3ae4b3f9e38cb7323696232aea00e3d3e04394ab1c7234"
    response = alchemy_with_key.get_transaction_by_hash(hash)
    assert response["from"].lower() == PATRICK_ALPHA_C.lower()


def test_get_transaction_by_block_hash_and_index(alchemy_with_key):
    hash = "0x50f4aaf5aa0e7f2be6766c406e542a42bc980b14f85500ee14f4873cb20d411c"
    index = 0
    expected_from = "0x6b2d93fc921a14928069f7f013addec1f61e329c"
    expected_to = "0x45511c17e28395d445b2992efff08ee65fe25146"
    response = alchemy_with_key.get_transaction_by_block_hash_and_index(hash, index)
    assert response["from"] == expected_from
    assert response["to"] == expected_to


def test_get_transaction_by_block_number_and_index(alchemy_with_key):
    number = 16292589
    index = 0
    expected_from = "0x6b2d93fc921a14928069f7f013addec1f61e329c"
    expected_to = "0x45511c17e28395d445b2992efff08ee65fe25146"
    response = alchemy_with_key.get_transaction_by_block_number_and_index(number, index)
    assert response["from"] == expected_from
    assert response["to"] == expected_to


def test_get_uncle_by_block_hash_and_index(alchemy_with_key):
    hash = "0xd6940190d24aa1c2e8aa70fb2847aba6c4461679753a7546daf79e6295a9e1e2"
    expected_miner = "0xea674fdde714fd979de3edf0f56aa9716b898ec8"
    expected_number = "0x1506f2"
    index = 0
    response = alchemy_with_key.get_uncle_by_block_hash_and_index(hash, index)
    assert response["miner"] == expected_miner
    assert response["number"] == expected_number


def test_get_uncle_by_block_number_and_index(alchemy_with_key):
    number = 1378035
    expected_miner = "0xea674fdde714fd979de3edf0f56aa9716b898ec8"
    expected_number = "0x1506f2"
    index = 0
    response = alchemy_with_key.get_uncle_by_block_number_and_index(number, index)
    assert response["miner"] == expected_miner
    assert response["number"] == expected_number


def test_client_version(alchemy_with_key):
    response = alchemy_with_key.client_version()
    assert response is not ""
    assert response is not None


def test_sha(alchemy_with_key):
    response = alchemy_with_key.sha("hi")
    expected_hash = "0x7624778dedc75f8b322b9fa1632a610d40b85e106c7d9bf0e743a9ce291b9c6f"
    assert response == expected_hash


def test_net_version(alchemy_with_key):
    response = alchemy_with_key.net_version()
    assert response == "1"


def test_net_listening(alchemy_with_key):
    response = alchemy_with_key.net_listening()
    assert response is True


# Not implemented in Alchemy
# def test_net_peer_count(alchemy_with_key):
#     response = alchemy_with_key.net_peer_count()


def test_protocol_version(alchemy_with_key):
    response = alchemy_with_key.protocol_version()
    assert HexIntStringNumber(response).int > 0


def test_syncing(alchemy_with_key):
    response = alchemy_with_key.syncing()
    assert response is False


# Not supported by Alchemy
# def test_coinbase(alchemy_with_key):
#     response = alchemy_with_key.coinbase()
#     assert response == "0x0000000000000000000000000000000000000000"

# Not supported by Alchemy
# def test_hashrate(alchemy_with_key):
#     response = alchemy_with_key.hashrate()
#     assert response == 0


def test_gas_price(alchemy_with_key):
    response = alchemy_with_key.gas_price()
    assert response > 0


# Unsupported by Alchemy
# def test_get_compilers(alchemy_with_key):
#     response = alchemy_with_key.get_compilers()
#     assert response == []


# Unsupported by Alchemy
# def test_get_work(alchemy_with_key):
#     response = alchemy_with_key.get_work()
#     assert response == []


def test_get_logs(alchemy_with_key):
    topics = ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]
    response = alchemy_with_key.get_logs(CHAINLINK_ADDRESS, topics, 16293070, 16293080)
    assert len(response) == 7
