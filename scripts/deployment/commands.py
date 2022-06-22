import brownie
from brownie import ZERO_ADDRESS, CMove, Contract, CWrap, Invoker

from data.access_control import APPROVED_COMMAND
from scripts.deployment import REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, DeployRegistryContainer

SUPPORTED_COMMANDS = [Invoker, CMove, CWrap]


def get_registry():
    registry_deployer = brownie.accounts.at(
        REGISTRY_DEPLOYER, force=True
    )  # for live, we get user from brownie keystore
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    return DeployRegistryContainer(
        registry_deployer, trusted_deployer, ensure_deployed=False
    )  # todo: need to set this to True for live


def _get_deployment_args(contract):
    if contract == Invoker:
        return [TRUSTED_DEPLOYER]
    elif contract == CWrap:
        return [ZERO_ADDRESS]
    else:
        return None


def deploy_and_approve_contract_if_not_deployed(
    registry: DeployRegistryContainer, contract: Contract
):
    if registry.is_deployed(contract):
        return registry.deployed_contract(contract)

    args = _get_deployment_args(contract)
    deployed_contract = registry.deploy(contract, args)

    if contract != Invoker:
        invoker = registry.deployed_contract(Invoker)
        invoker.grantRole(
            APPROVED_COMMAND, deployed_contract, {"from": registry.trusted_deployers[0]}
        )

    return deployed_contract


def main():
    registry = get_registry()
    for contract in SUPPORTED_COMMANDS:
        deploy_and_approve_contract_if_not_deployed(registry, contract)
