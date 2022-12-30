# Don't import anything into this file otherwise you'll do a circule import

NO_API_KEY_ERROR: str = (
    "A valid Alchemy API key must be provided "
    "either through the key parameter or "
    "through the environment variable "
    '"ALCHEMY_API_KEY". Get a free key '
    "from the alchemy website: "
    "https://alchemy.com/?a=673c802981"
)


def NETWORK_INITIALIZATION_ERROR(network_id_map):
    str = (
        "Network has been given a poor name or chain ID."
        f"Please use one of the following options: {network_id_map.keys()}"
    )
    return str
