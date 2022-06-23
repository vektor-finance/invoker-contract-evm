from brownie import (
    ZERO_ADDRESS,
    CMove,
    Contract,
    CSwapCurve,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CWrap,
    DeployerRegistry,
    Invoker,
    web3,
)
from eth_utils import keccak

from helpers.addresses import get_create1_address, get_create2_address

REGISTRY_DEPLOYER = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"  # hardcoded
TRUSTED_DEPLOYER = "0x70997970c51812dc3a010c7d01b50e0d17dc79c8"  # hardcoded

ALL_COMMANDS = [CMove, CWrap, CSwapUniswapV2, CSwapUniswapV3, CSwapCurve]
ALL_CONTRACTS = [Invoker, *ALL_COMMANDS]
CONTRACTS_TO_DEPLOY = ALL_CONTRACTS


class RegistryNotDeployedError(Exception):
    pass


class DeployRegistryContainer:
    def __init__(
        self, registry_deployer, trusted_deployer=ZERO_ADDRESS, ensure_deployed=False
    ) -> None:
        """
        Creates a DeployRegistryContainer

        If the DeployRegistry contract has been deployed, it uses this contract.
        If the DeployRegistry contract has not been deployed, it deploys a registry.
        """
        registry_deployer_address = (
            registry_deployer if type(registry_deployer) == str else registry_deployer.address
        )
        registry_address = get_create1_address(registry_deployer_address, 0)
        deployed_code = web3.eth.get_code(registry_address)

        if deployed_code == b"":
            if ensure_deployed:
                raise RegistryNotDeployedError
            # the deployer has not been deployed, deploy it
            assert trusted_deployer != ZERO_ADDRESS, "need to trust somebody to deploy!"
            self.contract: Contract = registry_deployer.deploy(DeployerRegistry, trusted_deployer)
            self.trusted_deployers = [trusted_deployer.address]
        else:
            # the deployer has been deployed, get the current contract
            self.contract: Contract = DeployerRegistry.at(registry_address)
            self.trusted_deployers = [trusted_deployer]

        self.registry_deployer = registry_deployer

    def get_deployment_args(self, contract):
        if contract == Invoker:
            return [TRUSTED_DEPLOYER]
        elif contract == CWrap:
            return [ZERO_ADDRESS]
        else:
            return None

    def _get_creation_code(self, contract, args):
        if args:
            return contract.deploy.encode_input(*args)
        return contract.bytecode

    def predict_deployment_address(self, contract):
        args = self.get_deployment_args(contract)
        creation_code = self._get_creation_code(contract, args)
        b_creation_code = bytes.fromhex(creation_code)
        init_code_hash = "0x" + keccak(b_creation_code).hex()
        predicted_address = get_create2_address(
            self.contract.address, self._get_salt_bytes(0), init_code_hash
        )
        return predicted_address

    def deploy(self, contract: Contract) -> Contract:
        args = self.get_deployment_args(contract)
        creation_code = self._get_creation_code(contract, args)
        tx = self.contract.deployNewContract(
            creation_code, "0", 0, {"from": self.trusted_deployers[0]}
        )
        deployed_contract = contract.at(tx.return_value)

        print(f"{contract._name} deployed at {deployed_contract.address}")

        return deployed_contract

    def _get_salt_bytes(self, salt: int):
        return "0x" + (salt).to_bytes(32, "big").hex()

    def is_deployed(self, contract: Contract) -> bool:
        predicted_address = self.predict_deployment_address(contract)
        deployed_code = web3.eth.get_code(predicted_address)
        return deployed_code != b""

    def get_deployed_contract(self, contract) -> Contract:
        predicted_address = self.predict_deployment_address(contract)
        return contract.at(predicted_address)

    def __repr__(self) -> str:
        return f"<DeployRegistry> {self.contract.address}"

    @classmethod
    def is_registry_deployed(cls):
        registry_address = get_create1_address(REGISTRY_DEPLOYER, 0)
        deployed_code = web3.eth.get_code(registry_address)
        return deployed_code != b""
