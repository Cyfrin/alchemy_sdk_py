from alchemy_sdk_py import set_api_key, get_current_block
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
