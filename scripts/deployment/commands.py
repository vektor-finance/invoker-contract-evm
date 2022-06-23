import brownie
from brownie import CMove, Contract, CSwapUniswapV2, CWrap, Invoker

from data.access_control import APPROVED_COMMAND
from scripts.deployment import REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, DeployRegistryContainer

SUPPORTED_COMMANDS = [Invoker, CMove, CWrap, CSwapUniswapV2]


def get_registry():
    registry_deployer = brownie.accounts.at(REGISTRY_DEPLOYER)
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER)

    return DeployRegistryContainer(
        registry_deployer, trusted_deployer, ensure_deployed=False
    )  # todo: need to set this to True for live


def deploy_and_approve_contract_if_not_deployed(
    registry: DeployRegistryContainer, contract: Contract
):

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
    for contract in SUPPORTED_COMMANDS:
        deploy_and_approve_contract_if_not_deployed(registry, contract)
