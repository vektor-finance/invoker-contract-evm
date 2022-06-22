from typing import Dict

from brownie import ZERO_ADDRESS, Contract, CWrap, DeployerRegistry, web3
from tabulate import tabulate

from helpers.addresses import get_create1_address

REGISTRY_DEPLOYER = "0x12331c2dDb0E841a40Bd5239365CE98F4b114e87"  # hardcoded
TRUSTED_DEPLOYER = "0xbeEf6e409E5374c15C50f60D07098aF846cB8178"  # hardcoded


class DeployRegistryContainer:
    def __init__(
        self, registry_deployer, trusted_deployer=ZERO_ADDRESS, ensure_deployed=False
    ) -> None:
        """
        Creates a DeployRegistryContainer

        If the DeployRegistry contract has been deployed, it uses this contract.
        If the DeployRegistry contract has not been deployed, it deploys a registry.
        """
        registry_address = get_create1_address(registry_deployer.address, 0)
        deployed_code = web3.eth.get_code(registry_address)

        if deployed_code == b"":
            assert not ensure_deployed, "Registry not deployed"
            # the deployer has not been deployed, deploy it
            assert trusted_deployer != ZERO_ADDRESS, "need to trust somebody to deploy!"
            self.contract: Contract = registry_deployer.deploy(DeployerRegistry, trusted_deployer)
            print(f"DeployRegistry deployed to {self.contract}")
            self.trusted_deployers = [trusted_deployer.address]
        else:
            # the deployer has been deployed, get the current contract
            print(f"DeployRegistry found at {registry_address}")
            self.contract: Contract = DeployerRegistry.at(registry_address)
            self.trusted_deployers = trusted_deployer

        self.registry_deployer = registry_deployer
        self.deployed_contracts: Dict[str, Contract] = {}

    def deploy(self, contract: Contract, args) -> Contract:
        creation_code = contract.bytecode
        if args:
            creation_code = contract.deploy.encode_input(*args)
        tx = self.contract.deployNewContract(
            creation_code, "0", 0, {"from": self.trusted_deployers[0]}
        )
        deployed_contract = contract.at(tx.return_value)

        self.deployed_contracts[contract._name] = deployed_contract

        return deployed_contract

    def is_deployed(self, contract: Contract) -> bool:
        return bool(self.deployed_contracts.get(contract._name))

    def _get_deployment_args(contract):
        if contract == CWrap:
            return [ZERO_ADDRESS]
        else:
            return None

    def deploy_all_contracts(self):
        # for contract in SUPPORTED_CONTRACTS:
        # self.deploy(contract, self._get_deployment_args(contract))
        self.print_deployments()

    def print_deployments(self):
        print(
            tabulate(
                [[self.contract, *self.deployed_contracts.values()]],
                headers=["Registry", *self.deployed_contracts.keys()],
                tablefmt="github",
            )
        )

    def deployed_contract(self, contract) -> Contract:
        return self.deployed_contracts[contract._name]

    def __repr__(self) -> str:
        return f"<DeployRegistry> {self.contract.address}"
