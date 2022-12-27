import os


def set_api_key(key: str):
    """
    params:
        key: API key
    returns:
        None
    """
    os.environ["ALCHEMY_API_KEY"] = key
