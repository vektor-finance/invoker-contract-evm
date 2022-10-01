from brownie import (
    ZERO_ADDRESS,
    CLendAave,
    CLendCompoundV3,
    CMove,
    Contract,
    Create2Deployer,
    CSwapCurve,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CWrap,
    Invoker,
    network,
    web3,
)
from eth_abi import encode_single
from eth_utils import keccak

from data.chain import get_chain_from_network_name, get_wnative_address
from helpers.addresses import get_create1_address, get_create2_address

REGISTRY_USER = "vektor_registry_deployer"
TRUSTED_USER = "vektor_trusted_deployer"

REGISTRY_DEPLOYER = "0xFB47e88C3FFF913D48F8EB08DdD96f86338E2568"  # hardcoded
TRUSTED_DEPLOYER = "0x3302dBdD355fDfA7A439598885E189a4E9ad6B9b"  # hardcoded

ALL_COMMANDS = [
    CMove,
    CWrap,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CSwapCurve,
    CLendAave,
    CLendCompoundV3,
]
ALL_CONTRACTS = [Invoker, *ALL_COMMANDS]
CONTRACTS_TO_DEPLOY = ALL_CONTRACTS


class RegistryNotDeployedError(Exception):
    pass


def strip_0x(hex_str: str):
    if hex_str.startswith("0x"):
        return hex_str[2:]
    return hex_str


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
            self.contract: Contract = registry_deployer.deploy(Create2Deployer, trusted_deployer)
            print(f"Gas used to deploy CREATE2: {self.contract.tx.gas_used}")
            self.trusted_deployers = [trusted_deployer.address]
        else:
            # the deployer has been deployed, get the current contract
            self.contract: Contract = Create2Deployer.at(registry_address)
            self.trusted_deployers = [trusted_deployer]
            print(f"CREATE2 Deployer was already found at {self.contract.address}")

        self.registry_deployer = registry_deployer

    def get_deployment_args(self, contract):
        if contract == Invoker:
            return encode_single("address", TRUSTED_DEPLOYER)
        elif contract == CWrap:
            (chain, _) = get_chain_from_network_name(network.show_active())
            wnative_address = get_wnative_address(chain)
            return encode_single("address", wnative_address)
        else:
            return "0x"

    def predict_deployment_address(self, contract):
        b_creation_code = bytes.fromhex(strip_0x(contract.bytecode))
        init_code_hash = "0x" + keccak(b_creation_code).hex()
        predicted_address = get_create2_address(
            self.contract.address, self._get_salt_bytes(0), init_code_hash
        )
        return predicted_address

    def deploy(self, contract: Contract) -> Contract:
        args = self.get_deployment_args(contract)
        tx = self.contract.deployNewContract(
            contract.bytecode, "0", 0, args, {"from": self.trusted_deployers[0]}
        )
        deployed_contract = self.predict_deployment_address(contract)
        gas_used = tx.gas_used

        print(f"{contract._name} deployed at {deployed_contract}")

        return deployed_contract, gas_used

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
