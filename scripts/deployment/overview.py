from brownie import Invoker, network
from brownie.exceptions import ContractNotFound
from tabulate import tabulate

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_id
from scripts.deployment import (
    ALL_CONTRACTS,
    REGISTRY_DEPLOYER,
    TRUSTED_DEPLOYER,
    DeployRegistryContainer,
    chain_id_to_contracts,
)


def get_network_deployment_info():
    registry_deployed = DeployRegistryContainer.is_registry_deployed()

    network_deployments = {"Network": network.show_active()}

    registry = None
    if registry_deployed:
        registry = DeployRegistryContainer(
            REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, ensure_deployed=True
        )
        network_deployments["Registry"] = registry.contract.address
    else:
        network_deployments["Registry"] = "NO REGISTRY DEPLOYED"

    chain_id = get_chain_id()
    contracts_to_deploy = chain_id_to_contracts(chain_id)

    for contract in ALL_CONTRACTS:
        if not registry:
            network_deployments[contract._name] = "-"
            continue

        if contract != Invoker and contract not in contracts_to_deploy:
            network_deployments[contract._name] = "🚫 not required"
            continue

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

            network_deployments[contract._name] = status + deployed_contract.address
        except ContractNotFound:
            network_deployments[contract._name] = "🚧 not deployed"

    return network_deployments


def main():
    hardhat_table = get_network_deployment_info()
    data = list(hardhat_table.items())
    table = tabulate(data, tablefmt="grid")
    print(table)
