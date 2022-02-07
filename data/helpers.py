import os

import yaml


def get_chain_data():
    with open(os.path.join("data", "chains.yaml"), "r") as file:
        return yaml.safe_load(file)


def get_chain_from_network_name(network_name):
    data = get_chain_data()
    chain = next(
        (data[chain] for chain in data if network_name in data[chain]["network"].values()), None
    )
    network = chain["network"]
    mode = next(k for k in network if network[k] == network_name)
    return (chain, mode)
