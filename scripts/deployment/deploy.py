import brownie
from brownie import Contract, Invoker

from data.access_control import APPROVED_COMMAND
from scripts.deployment import (
    CONTRACTS_TO_DEPLOY,
    REGISTRY_DEPLOYER,
    TRUSTED_USER,
    DeployRegistryContainer,
    overview,
)


def get_registry():
    registry_deployer = brownie.accounts.at(REGISTRY_DEPLOYER, force=True)
    trusted_deployer = brownie.accounts.load(TRUSTED_USER)

    return DeployRegistryContainer(registry_deployer, trusted_deployer)


def deploy_and_approve_contract_if_not_deployed(
    registry: DeployRegistryContainer, contract: Contract
):
    print(f"Trying to deploy {contract._name}")

    if registry.is_deployed(contract):
        print(f"{contract._name} already deployed. Skipping")
        return registry.get_deployed_contract(contract)

    deployed_contract, gas_used = registry.deploy(contract)

    if contract != Invoker:
        invoker = registry.get_deployed_contract(Invoker)
        tx = invoker.grantRole(
            APPROVED_COMMAND, deployed_contract, {"from": registry.trusted_deployers[0]}
        )
        gas_used += tx.gas_used

    print(f"{contract._name} has been deployed and approved.")

    return deployed_contract, gas_used


def main():
    cumulative_gas = 0
    registry = get_registry()
    for contract in CONTRACTS_TO_DEPLOY:
        _, gas_used = deploy_and_approve_contract_if_not_deployed(registry, contract)
        cumulative_gas += gas_used

    print(f"Total Gas Used: {cumulative_gas}")

    overview.main()
