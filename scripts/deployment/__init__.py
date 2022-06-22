from typing import Dict

from brownie import ZERO_ADDRESS, Contract, DeployerRegistry, web3
from eth_utils import keccak
from tabulate import tabulate

from helpers.addresses import get_create1_address, get_create2_address

REGISTRY_DEPLOYER = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"  # hardcoded
TRUSTED_DEPLOYER = "0x70997970c51812dc3a010c7d01b50e0d17dc79c8"  # hardcoded


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
            self.trusted_deployers = [trusted_deployer]

        self.registry_deployer = registry_deployer
        self.deployed_contracts: Dict[str, Contract] = {}

    def _get_creation_code(self, contract, args):
        if args:
            return contract.deploy.encode_input(*args)
        return contract.bytecode

    def deploy(self, contract: Contract, args) -> Contract:
        creation_code = self._get_creation_code(contract, args)
        tx = self.contract.deployNewContract(
            creation_code, "0", 0, {"from": self.trusted_deployers[0]}
        )
        deployed_contract = contract.at(tx.return_value)

        self.deployed_contracts[contract._name] = deployed_contract

        print(f"{contract._name} deployed at {deployed_contract.address}")

        return deployed_contract

    def _get_salt_bytes(self, salt: int):
        return "0x" + (salt).to_bytes(32, "big").hex()

    def is_deployed(self, contract: Contract, args) -> bool:
        creation_code = self._get_creation_code(contract, args)
        b_creation_code = bytes.fromhex(creation_code)
        init_code_hash = "0x" + keccak(b_creation_code).hex()
        predicted_address = get_create2_address(
            self.contract.address, self._get_salt_bytes(0), init_code_hash
        )
        deployed_code = web3.eth.get_code(predicted_address)
        return deployed_code != b""

    def print_deployments(self):
        print(
            tabulate(
                [[self.contract, *self.deployed_contracts.values()]],
                headers=["Registry", *self.deployed_contracts.keys()],
                tablefmt="github",
            )
        )

    def deployed_contract(self, contract, args=None) -> Contract:
        creation_code = self._get_creation_code(contract, args)
        b_creation_code = bytes.fromhex(creation_code)
        init_code_hash = "0x" + keccak(b_creation_code).hex()
        predicted_address = get_create2_address(
            self.contract.address, self._get_salt_bytes(0), init_code_hash
        )
        return contract.at(predicted_address)

    def __repr__(self) -> str:
        return f"<DeployRegistry> {self.contract.address}"
