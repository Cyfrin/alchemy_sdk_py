from alchemy_sdk_py import set_api_key, get_current_block, get_asset_transfers
import os


def test_set_api_key():
    # Arrange
    del os.environ["ALCHEMY_API_KEY"]
    # Act
    set_api_key("Hello")
    # Assert
    assert os.getenv("ALCHEMY_API_KEY") == "Hello"


def test_get_current_block():
    # Arrange / Act
    current_block = get_current_block()

    # Assert
    assert current_block > 0


def test_get_asset_transfers_page_key():
    # Arrange
    start_block = 0
    end_block = 16271807
    address = "0x165Ff6730D449Af03B4eE1E48122227a3328A1fc"

    # Act
    _, page_key = get_asset_transfers(address, start_block, end_block)

    # Assert
    assert page_key is not None


def test_get_asset_transfers_page_key_is_none():
    # Arrange
    start_block = 16271807
    end_block = 16271807
    address = "0x165Ff6730D449Af03B4eE1E48122227a3328A1fc"

    # Act
    _, page_key = get_asset_transfers(address, start_block, end_block)

    # Assert
    assert page_key is None
