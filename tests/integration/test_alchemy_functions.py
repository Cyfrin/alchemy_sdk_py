from alchemy_sdk_py import Alchemy
import os


def test_set_api_key(alchemy, mock_env_missing):
    # Arrange / Act
    alchemy.set_api_key("Hello")
    # Assert
    assert alchemy.api_key == "Hello"


def test_get_current_block(alchemy_with_key):
    # Arrange / Act
    current_block = alchemy_with_key.get_current_block()
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
