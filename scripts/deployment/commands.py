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
    brownie.accounts[0].transfer(trusted_deployer, 10e18)

    return DeployRegistryContainer(registry_deployer, trusted_deployer)


def deploy_and_approve_contract_if_not_deployed(
    registry: DeployRegistryContainer, contract: Contract
):
    print(f"Trying to deploy {contract._name}")

    if registry.is_deployed(contract):
        print(f"{contract._name} already deployed. Skipping")
        return registry.get_deployed_contract(contract)

    deployed_contract = registry.deploy(contract)

    if contract != Invoker:
        invoker = registry.get_deployed_contract(Invoker)
        invoker.grantRole(
            APPROVED_COMMAND, deployed_contract, {"from": registry.trusted_deployers[0]}
        )

    print(f"{contract._name} has been deployed and approved.")

    return deployed_contract


def main():
    registry = get_registry()
    for contract in CONTRACTS_TO_DEPLOY:
        deploy_and_approve_contract_if_not_deployed(registry, contract)

    overview.main()
