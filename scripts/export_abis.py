import json

from brownie import CMove, CSwap, Invoker

contracts = [CMove, CSwap, Invoker]


def main():
    for contract in contracts:
        with open(f"{contract._name}.json", "w") as contract_file:
            json.dump(contract.abi, contract_file, indent=2)
