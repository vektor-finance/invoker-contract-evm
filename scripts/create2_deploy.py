from typing import List

from brownie import CMove, Contract, Invoker, web3
from tabulate import tabulate

from data.chain import get_all_chain_names  # , get_chain_data
from helpers.addresses import get_create1_address
from helpers.network_switcher import NetworkSwitcher

REGISTRY_DEPLOYER = "0x0fbC5562670d73b060C44Bb6085d39AA628624BE"
REGISTRY_ADDRESS = get_create1_address(REGISTRY_DEPLOYER, 0)
SUPPORTED_CONTRACTS: List[Contract] = [Invoker, CMove]

print(REGISTRY_ADDRESS)


def get_network_registry(network):
    return "no registry"


def get_brownie_network_name(chains, network, use_fork=True):
    chain = chains[network]
    if use_fork:
        return chain["network"]["fork"]
    else:
        return chain["network"]["prod"]


def get_network_contracts(chains, network):
    contract_addresses = []
    registry = get_network_registry(network)
    network_name = get_brownie_network_name(chains, network)
    with NetworkSwitcher(network_name, False):
        for contract in SUPPORTED_CONTRACTS:
            available_code = web3.eth.get_code("0xab7ce6C76E985792f80339183327C3F7A0B78E57")
            print(available_code.hex())
            contract_addresses.append(available_code.hex())
    return [registry, *contract_addresses]


def get_network_headers():
    return ["Network", "Registry", *[contract._name for contract in SUPPORTED_CONTRACTS]]


def main():
    # chains = get_chain_data()
    supported_networks = get_all_chain_names()
    data = []
    # print(f"Supported networks: {supported_networks}")
    for network in supported_networks:
        # data.append([network, *get_network_contracts(chains, network)])
        data.append(["-", "-", "-", "-"])
    print(tabulate(data, headers=get_network_headers()))
    pass
