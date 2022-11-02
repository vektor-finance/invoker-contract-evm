from brownie import Invoker, network
from brownie.exceptions import ContractNotFound
from tabulate import tabulate

from data.access_control import APPROVED_COMMAND
from scripts.deployment import (
    ALL_CONTRACTS,
    REGISTRY_DEPLOYER,
    TRUSTED_DEPLOYER,
    DeployRegistryContainer,
)


def shorten_address(address):
    return address[0:6] + "..." + address[-4:]


def get_network_deployment_info():
    registry_deployed = DeployRegistryContainer.is_registry_deployed()

    network_deployments = {"network": network.show_active()}

    registry = None
    if registry_deployed:
        registry = DeployRegistryContainer(
            REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, ensure_deployed=True
        )
        network_deployments["registry"] = shorten_address(registry.contract.address)
    else:
        network_deployments["registry"] = "NO REGISTRY DEPLOYED"

    for contract in ALL_CONTRACTS:
        if registry:
            try:
                status = ""
                deployed_contract = registry.get_deployed_contract(contract)
                if contract != Invoker:
                    is_approved = False
                    try:
                        invoker = registry.get_deployed_contract(Invoker)
                        is_approved = invoker.hasRole(APPROVED_COMMAND, deployed_contract.address)
                    except ContractNotFound:
                        pass
                    status = "✅ " if is_approved else "❌ "
                network_deployments[contract._name] = status + shorten_address(
                    deployed_contract.address
                )
            except ContractNotFound:
                network_deployments[contract._name] = "not deployed"
        else:
            network_deployments[contract._name] = "-"

    return network_deployments


def main():

    deployment_table = []

    hardhat_table = get_network_deployment_info()
    deployment_table.append(hardhat_table)

    print(tabulate(deployment_table, headers="keys", tablefmt="github"))
