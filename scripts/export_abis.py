import json
import os

from brownie import CMove, CSwap, Invoker

contracts = [CMove, CSwap, Invoker]

OUTPUTS_ABIS_DIR = "outputs/abi"


def main():
    if not os.path.exists(OUTPUTS_ABIS_DIR):
        os.makedirs(OUTPUTS_ABIS_DIR)

    for contract in contracts:
        with open(f"{OUTPUTS_ABIS_DIR}/{contract._name}.json", "w") as contract_file:
            json.dump(contract.abi, contract_file, indent=2)
