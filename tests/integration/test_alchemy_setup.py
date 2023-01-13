from alchemy_sdk_py import Alchemy
import os
import pytest


def test_initialize_empty_network(dummy_api_key, mock_env_missing):
    alchemy = Alchemy(api_key=dummy_api_key)
    assert alchemy.network == "eth_mainnet"


def test_initialize_network_by_name(dummy_api_key):
    alchemy = Alchemy(api_key=dummy_api_key, network="eth_ropsten")
    assert alchemy.network == "eth_ropsten"


def test_initialize_network_by_str_chain_id(dummy_api_key):
    alchemy = Alchemy(api_key=dummy_api_key, network="5")
    assert alchemy.network == "eth_goerli"


def test_initialize_network_by_int_chain_id(dummy_api_key):
    alchemy = Alchemy(api_key=dummy_api_key, network=5)
    assert alchemy.network == "eth_goerli"


def test_initialize_network_by_bad_network(dummy_api_key):
    with pytest.raises(ValueError):
        _ = Alchemy(api_key=dummy_api_key, network=2)


def test_initialize_alchemy_using_key_instead_of_api_key(dummy_api_key):
    alchemy = Alchemy(key=dummy_api_key, network=5)
    assert alchemy.api_key == dummy_api_key


def test_api_key_property(dummy_api_key):
    alchemy = Alchemy(api_key=dummy_api_key, network=5)
    assert alchemy.key == dummy_api_key


def test_key_with_environment_variable():
    test_key = "test_key"
    original_value = os.environ["ALCHEMY_API_KEY"]
    os.environ["ALCHEMY_API_KEY"] = test_key
    alchemy = Alchemy()
    assert alchemy.key == test_key
    os.environ["ALCHEMY_API_KEY"] = original_value
