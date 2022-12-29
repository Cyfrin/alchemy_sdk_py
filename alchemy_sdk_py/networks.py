from .errors import NETWORK_INITIALIZATION_ERROR
from typing import Union
from .sdk_settings import network_id_map


class Network:
    def __init__(self, name_or_chain_id: Union[str, int, None] = "eth_mainnet"):
        """Creates an instance of a Network class, which is an easy way to access the chain ID and name of a network.

        Args:
            name_or_chain_id (Union[str, int, None], optional): This can be one of the following:
            - A chain name, ie: "eth_mainnet"
            - A chain ID, ie: 1
            - A hex chain ID, ie: "0x1"
            - A chain ID as a string, ie: "1"
            - None, which goes to the default

            Defaults to "eth_mainnet".

        Raises:
            ValueError: If the network name or chain ID is not valid.
        """
        name_or_chain_id = str(name_or_chain_id)
        if name_or_chain_id.startswith("0x"):
            name_or_chain_id = str(int(name_or_chain_id, 16))
        if name_or_chain_id not in network_id_map:
            raise ValueError(NETWORK_INITIALIZATION_ERROR)
        else:
            if name_or_chain_id.isdigit():
                self.chain_id = name_or_chain_id
                self.name = network_id_map[name_or_chain_id]
            else:
                self.name = name_or_chain_id
                self.chain_id = network_id_map[name_or_chain_id]

    def __eq__(self, other: Union[str, int]):
        other = str(other)
        return self.name == other or self.chain_id == other
