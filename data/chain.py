import os

import yaml


def get_chain_data():
    with open(os.path.join("data", "chains.yaml"), "r") as file:
        return yaml.safe_load(file)


def get_chain_from_network_name(network_name):
    """Returns 'chain' object from network name
    network_name specifically refers to the network name according to brownie
    """
    data = get_chain_data()

    def generator(data):
        for chain in data:
            if network_name in data[chain]["network"].values():
                yield data[chain]

    chain = next(generator(data))

    def mode_generator(chain):
        for key in chain["network"]:
            if chain["network"][key] == network_name:
                yield key

    mode = next(mode_generator(chain))

    return (chain, mode)


def get_weth_address(chain):
    """Get the first WETH address from chain
    Does this by checking for wrapped_native
    If multiple assets exists, it returns the first
    """

    def generator(chain):
        tokens = chain["assets"]
        for token in tokens:
            if token.get("wrapped_native"):
                yield token

    return next(generator(chain))["address"]


def get_uni_router_address(chain):
    """Get the first uniswap router
    Does this by checking interfaces
    If multiple routers exist, it returns the first
    """

    def generator(chain):
        contracts = chain["contracts"]
        for contract in contracts:
            if "uniswap_router_v2_02" in contract["interfaces"]:
                yield contract

    return next(generator(chain))["address"]
