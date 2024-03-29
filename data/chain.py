import os
import sys

import yaml
from brownie._config import CONFIG


def get_chain_data():
    with open(os.path.join("data", "chains.yaml"), "r") as file:
        return yaml.safe_load(file)


def get_all_chain_names():
    data = get_chain_data()
    return list(data.keys())


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


def get_wnative_address(chain):
    """Get the first wrapped native address from chain
    Does this by checking for wrapped_native
    If multiple assets exists, it returns the first
    """

    def generator(chain):
        tokens = chain["assets"]
        for token in tokens:
            if token.get("wrapped_native"):
                yield token

    return next(generator(chain))["address"].lower()


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

    return next(generator(chain))["address"].lower()


CHAINS = {
    "1": "mainnet",
    "56": "binance smart chain",
    "66": "okex chain",
    "137": "polygon",
    "42161": "arbitrum",
    "43114": "avalanche",
    "250": "fantom",
    "128": "huobi eco",
    "25": "cronos mainnet beta",
    "40": "telos evm",
    "288": "boba network",
    "1088": "metis andromeda",
    "42220": "celo mainnet",
    "1313161554": "aurora mainnet",
    "1666600000": "harmony mainnet",
    "1284": "moonbeam",
}


def get_chain_name(chain_id):
    return CHAINS.get(str(chain_id))


def get_network():
    # Difficult to get network before brownie is connected
    # This is a hack/workaround to get the default network
    # Or the network specificed in the CLI.
    network = CONFIG.settings["networks"]["default"]
    if CONFIG.argv["network"]:
        network = CONFIG.argv["network"]
    else:
        try:
            _net = sys.argv.index("--network")
            network = sys.argv[_net + 1]
        except ValueError:
            pass
    return network


def get_chain():
    connected_network = get_network()
    (chain, _) = get_chain_from_network_name(connected_network)
    return chain


def get_chain_id():
    chain = get_chain()
    return chain["chain_id"]


def is_uniswapv3_on_chain(chain):
    for contract in chain["contracts"]:
        if "uniswap_router_v3" in contract["interfaces"]:
            return True
    return False


def is_venue_on_chain(venue, chain):
    assert venue in [
        "aave_v2",
        "aave_v3",
        "uniswap_v3",
        "uniswap",
        "sushiswap",
    ], "unrecognised venue"
    for contract in chain["contracts"]:
        if venue == contract["venue"]:
            return contract["address"]
    return None


def get_chain_tokens():
    chain = get_chain()
    return chain["assets"]


def get_chain_token(symbol: str):
    tokens = get_chain_tokens()
    return [a for a in tokens if a["symbol"] == symbol.upper()][0]
