from brownie import ZERO_ADDRESS, Contract, CWrap, DeployerRegistry, web3
from tabulate import tabulate

from helpers.addresses import get_create1_address


class DeployRegistryContainer:
    def __init__(self, registry_deployer, trusted_deployer=ZERO_ADDRESS) -> None:
        """
        Creates a DeployRegistryContainer

        If the DeployRegistry contract has been deployed, it uses this contract.
        If the DeployRegistry contract has not been deployed, it deploys a registry.
        """
        registry_address = get_create1_address(registry_deployer.address, 0)
        deployed_code = web3.eth.get_code(registry_address)

        if deployed_code == b"":
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
        self.deployed_contracts = {}

    def deploy(self, contract: Contract, args):
        creation_code = contract.bytecode
        if args:
            creation_code = contract.deploy.encode_input(*args)
        tx = self.contract.deployNewContract(
            creation_code, "0", 0, {"from": self.trusted_deployers[0]}
        )
        deployed_contract = contract.at(tx.return_value)

        self.deployed_contracts[contract._name] = deployed_contract

        return deployed_contract

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

    def __repr__(self) -> str:
        return f"<DeployRegistry> {self.contract.address}"
