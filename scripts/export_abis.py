import json
import os

from brownie.project import InvokerContractEvmProject

# from brownie.project.build import Build

contracts = InvokerContractEvmProject.dict()

OUTPUTS_ABIS_DIR = "outputs/abi"


def main():
    if not os.path.exists(OUTPUTS_ABIS_DIR):
        os.makedirs(OUTPUTS_ABIS_DIR)

    b = InvokerContractEvmProject._build

    for contract_name in contracts:
        contract = b.get(contract_name=contract_name)
        with open(f"{OUTPUTS_ABIS_DIR}/{contract['contractName']}.json", "w") as contract_file:
            json.dump(contract["abi"], contract_file, indent=2)
