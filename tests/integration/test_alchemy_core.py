PATRICK_ALPHA_C = "0x874437B5a42aA6E6419eC2447C9e36c278c46532"
VITALIK = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
GAS = "0x76c0"
GAS_PRICE = "0x9184e72a000"
VALUE = 0
DATA = "0x3b3b57debf074faa138b72c65adbdcfb329847e4f2c04bde7f7dd7fcad5a52d2f395a558"
TAG = "latest"
CHAINLINK = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
CHAINLINK_CREATOR = "0xf55037738604FDDFC4043D12F25124E94D7D1780"


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


# def test_get_balance(alchemy_with_key):
#     response = alchemy_with_key.get_balance(PATRICK_ALPHA_C, TAG)
#     # Only true if Patrick's ass ain't broke
#     assert response > 0


def test_get_block(alchemy_with_key):
    response = alchemy_with_key.get_block(0)
    breakpoint()
