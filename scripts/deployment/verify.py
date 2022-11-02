import json
import time
from pathlib import Path

import brownie
from brownie import CLendAave, CLendCompoundV3
from brownie.network.contract import ContractContainer

from scripts.deployment import (
    ALL_CONTRACTS,
    REGISTRY_DEPLOYER,
    TRUSTED_DEPLOYER,
    DeployRegistryContainer,
)


def is_modified():
    modified = False
    try:
        venv = Path(brownie.__file__).parent.parent
        installed = venv / "eth_brownie-1.19.2.dist-info" / "direct_url.json"
        with installed.open("r") as infile:
            data = json.load(infile)
            if data["url"] == "https://github.com/vektor-finance/brownie.git":
                modified = True
    except FileNotFoundError:
        pass
    return modified


def verify_contract(contract: ContractContainer, address: str):
    print(f"Attempting to verify {contract._name} at {address}")
    to_verify = contract.at(address)
    assert contract.get_verification_info()["license_identifier"].lower() == "unlicensed"
    try:
        contract.publish_source(to_verify)
        time.sleep(5)  # don't throttle API
    except ValueError as e:
        msg = e.args[0]
        if "Contract source code already verified" not in msg:
            raise e from None
        print(f"Already verified {contract._name}")


def main():
    if is_modified():
        registry = DeployRegistryContainer(
            REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, ensure_deployed=True
        )
        for contract in ALL_CONTRACTS:
            if contract not in [
                CLendAave,
                CLendCompoundV3,
            ]:  # can't verify vyper contracts via etherscan API
                verify_contract(contract, registry.get_deployed_contract(contract))
            else:
                print(
                    f"Need to manually verify {contract._name} at "
                    f"{registry.get_deployed_contract(contract)}"
                )
    else:
        print("Not using patched version of brownie")
        print(
            "Please ensure you are in a virtualenv"
            + " and have configured pip to install vektor-finance/brownie"
        )
