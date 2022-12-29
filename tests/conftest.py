import pytest
from alchemy_sdk_py import Alchemy
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def dummy_api_key() -> str:
    return "Hello"


@pytest.fixture
def alchemy(dummy_api_key: str) -> Alchemy:
    return Alchemy(dummy_api_key)


@pytest.fixture
def alchemy_with_key() -> Alchemy:
    # Be sure to use an environment variable called ALCHEMY_API_KEY
    return Alchemy()


@pytest.fixture
def mock_env_missing(monkeypatch: MonkeyPatch):
    """A plugin from pytest to help saftely mock and delete environment variables.

    Args:
        monkeypatch (_pytest.monkeypatch.MonkeyPatch): _description_
    """
    monkeypatch.delenv("ALCHEMY_API_KEY", raising=False)
