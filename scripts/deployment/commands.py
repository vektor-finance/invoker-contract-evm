import brownie
from brownie import ZERO_ADDRESS, CMove, Contract, CSwapUniswapV2, CWrap, Invoker

from data.access_control import APPROVED_COMMAND
from scripts.deployment import REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, DeployRegistryContainer

SUPPORTED_COMMANDS = [Invoker, CMove, CWrap, CSwapUniswapV2]


def get_registry():
    registry_deployer = brownie.accounts.at(REGISTRY_DEPLOYER, force=True)
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
    args = _get_deployment_args(contract)

    if registry.is_deployed(contract, args):
        print(f"{contract._name} already deployed. Skipping")
        return registry.deployed_contract(contract, args)

    deployed_contract = registry.deploy(contract, args)

    if contract != Invoker:
        invoker = registry.deployed_contract(Invoker, _get_deployment_args(Invoker))
        invoker.grantRole(
            APPROVED_COMMAND, deployed_contract, {"from": registry.trusted_deployers[0]}
        )

    print(f"{contract._name} has been deployed and approved.")

    return deployed_contract


def main():
    registry = get_registry()
    for contract in SUPPORTED_COMMANDS:
        deploy_and_approve_contract_if_not_deployed(registry, contract)


"Invoker deployed at 0xac11291dC6Cc1036104B8Fe608d4FF038Fc49950"
"Deployed bytecode hash bd2e09551aa0dddd9924878c5645013c0490442b677a068c6731b8ae1b513c0e"
