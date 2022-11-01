import json
from pathlib import Path

import brownie
from brownie.network.contract import ContractContainer


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
    to_verify = contract.at(address)
    assert contract.get_verification_info()["license_identifier"].lower() == "unlicensed"
    contract.publish_source(to_verify)


def main():
    if is_modified():
        # need to actually add arguments here
        verify_contract()
    else:
        print("Not using patched version of brownie")
        print(
            "Please ensure you are in a virtualenv"
            + " and have configured pip to install vektor-finance/brownie"
        )
