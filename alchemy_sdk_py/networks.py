from .errors import NETWORK_INITIALIZATION_ERROR
from typing import Union

network_id_map = {
    "eth_mainnet": "1",
    "eth_ropsten": "3",
    "eth_rinkeby": "4",
    "eth_goerli": "5",
    "eth_kovan": "42",
    "opt_mainnet": "10",
    "opt_goerli": "420",
    "arb_mainnet": "42161",
    "arb_rinkeby": "421611",
    "matic_mainnet": "137",
    "matic_mumbai": "80001",
    "astar_mainnet": "592",
    "1": "eth_mainnet",
    "3": "eth_ropsten",
    "4": "eth_rinkeby",
    "5": "eth_goerli",
    "42": "eth_kovan",
    "10": "opt_mainnet",
    "420": "opt_goerli",
    "42161": "arb_mainnet",
    "421611": "arb_rinkeby",
    "137": "matic_mainnet",
    "80001": "matic_mumbai",
    "592": "astar_mainnet",
}


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
            raise ValueError(NETWORK_INITIALIZATION_ERROR(network_id_map))
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
