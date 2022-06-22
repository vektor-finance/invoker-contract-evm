from typing import List

import brownie
from brownie import (
    ZERO_ADDRESS,
    CLPCurve,
    CLPUniswapV2,
    CLPUniswapV3,
    CMove,
    Contract,
    CSwapCurve,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CWrap,
    Invoker,
    accounts,
)
from tabulate import tabulate

from data.chain import get_all_chain_names, get_chain_data
from helpers.network_switcher import NetworkSwitcher
from scripts.deployment import DeployRegistryContainer

SUPPORTED_CONTRACTS: List[Contract] = [
    Invoker,
    CMove,
    CWrap,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CSwapCurve,
    CLPUniswapV2,
    CLPUniswapV3,
    CLPCurve,
]


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
            contract_addresses.append(contract._name)
    return [registry, *contract_addresses]


def get_network_headers():
    return ["Network", "Registry", *[contract._name for contract in SUPPORTED_CONTRACTS]]


def old_main():
    chains = get_chain_data()
    supported_networks = get_all_chain_names()
    supported_networks = ["dev"]
    data = []
    for network in supported_networks:
        data.append([network, *get_network_contracts(chains, network)])
    print(tabulate(data, headers=get_network_headers()))


def _get_deployment_args(contract):
    if contract == CWrap:
        return [ZERO_ADDRESS]
    else:
        return None


def main():
    REGISTRY_DEPLOYER = "0x12331c2dDb0E841a40Bd5239365CE98F4b114e87"
    TRUSTED_DEPLOYER = "0xbeEf6e409E5374c15C50f60D07098aF846cB8178"
    assert brownie.network.show_active() == "hardhat"
    registry_deployer = accounts.at(REGISTRY_DEPLOYER, force=True)
    trusted_deployer = accounts.at(TRUSTED_DEPLOYER, force=True)

    registry = DeployRegistryContainer(registry_deployer, trusted_deployer)
    registry.deploy_all_contracts()
