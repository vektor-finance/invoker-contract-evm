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
    DeployerRegistry,
    Invoker,
    accounts,
)
from tabulate import tabulate

from data.chain import get_all_chain_names, get_chain_data
from helpers.addresses import get_create1_address
from helpers.network_switcher import NetworkSwitcher

REGISTRY_DEPLOYER = "0x0fbC5562670d73b060C44Bb6085d39AA628624BE"
REGISTRY_ADDRESS = get_create1_address(REGISTRY_DEPLOYER, 0)
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


class DeployRegistryContainer:
    def __init__(self, contract: Contract, deployer) -> None:
        self.contract: Contract = contract
        self.deployer = deployer
        self.deployed_contracts = {}

    def deploy(self, contract: Contract, args):
        creation_code = contract.bytecode
        if args:
            creation_code = contract.deploy.encode_input(*args)
        tx = self.contract.deployNewContract(creation_code, "0", 0, {"from": self.deployer})
        deployed_contract = contract.at(tx.return_value)

        self.deployed_contracts[contract._name] = deployed_contract

        return deployed_contract

    def print_deployments(self):
        print(
            tabulate(
                [[self.contract, *self.deployed_contracts.values()]],
                headers=["Registry", *self.deployed_contracts.keys()],
                tablefmt="github",
            )
        )

    @classmethod
    def create_from(cls, deployer):
        return cls(deployer.deploy(DeployerRegistry), deployer)

    def __repr__(self) -> str:
        return f"<DeployRegistry> {self.contract.address}"


def _get_deployment_args(contract):
    if contract == CWrap:
        return [ZERO_ADDRESS]
    else:
        return None


def deploy_all_contracts(deployer):
    registry = DeployRegistryContainer.create_from(deployer)
    for contract in SUPPORTED_CONTRACTS:
        registry.deploy(contract, _get_deployment_args(contract))
    registry.print_deployments()


def main():
    assert brownie.network.show_active() == "hardhat"
    deployer = accounts.at("0x12331c2dDb0E841a40Bd5239365CE98F4b114e87", force=True)
    deploy_all_contracts(deployer)
