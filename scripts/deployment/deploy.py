import brownie
from brownie import Contract, Invoker

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_id
from scripts.deployment import (
    CONTRACTS_TO_DEPLOY,
    REGISTRY_DEPLOYER,
    TRUSTED_DEPLOYER,
    TRUSTED_USER,
    DeployRegistryContainer,
    chain_id_to_contracts,
)


def get_registry():
    registry_deployer = brownie.accounts.at(REGISTRY_DEPLOYER, force=True)
    try:
        trusted_deployer = brownie.accounts.load(TRUSTED_USER)
    except FileNotFoundError:
        trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    return DeployRegistryContainer(registry_deployer, trusted_deployer)


def deploy_and_approve_contract_if_not_deployed(
    registry: DeployRegistryContainer, contract: Contract
):
    chain_id = get_chain_id()
    contracts_to_deploy = chain_id_to_contracts(chain_id)

    if contract != Invoker and contract not in contracts_to_deploy:
        print(f"{contract._name} not required.")
        return None, 0

    if registry.is_deployed(contract):
        print(f"{contract._name} already deployed. Skipping")
        deployed_contract, gas_used = registry.get_deployed_contract(contract), 0
    else:
        print(f"Trying to deploy {contract._name}")
        deployed_contract, gas_used = registry.deploy(contract)

    if contract != Invoker:
        invoker = registry.get_deployed_contract(Invoker)
        is_approved = invoker.hasRole(APPROVED_COMMAND, deployed_contract)
        if not is_approved:
            tx = invoker.grantRole(
                APPROVED_COMMAND, deployed_contract, {"from": registry.trusted_deployers[0]}
            )
            gas_used += tx.gas_used
            print(f"{contract._name} has been approved to use with Invoker.")

    return deployed_contract, gas_used


def main():
    cumulative_gas = 0
    registry = get_registry()
    for contract in CONTRACTS_TO_DEPLOY:
        _, gas_used = deploy_and_approve_contract_if_not_deployed(registry, contract)
        cumulative_gas += gas_used

    print(f"Total Gas Used: {cumulative_gas}")
