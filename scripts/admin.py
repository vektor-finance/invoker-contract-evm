import json
import os
import sys

import brownie
from brownie import Contract, Invoker, accounts, network

from data.access_control import ROLE_PAUSER
from data.chain import get_chain_from_network_name

block_number = 0


def get_opts(user, chain):
    gas_override = os.environ.get("GAS_GWEI")
    if gas_override:
        return {"from": user, "gas_price": f"{gas_override} gwei"}
    if chain.get("eip1559"):
        return {"from": user, "priority_fee": "2 gwei"}
    else:
        return {"from": user}


def get_invoker_chainid(chain_id):
    global block_number
    with open(os.path.join("deployments", "deployments.json"), "r") as infile:
        deployments = json.load(infile)
    contracts = deployments[str(chain_id)]
    invokers = [contract for contract in contracts if contract["contract"] == "Invoker"]
    if len(invokers) == 0:
        print("No deployed invoker found")
        return None
    elif len(invokers) == 1:
        print(f"Invoker contract deployed at {invokers[0]['address']}")
        block_number = invokers[0]["block_number"]
        return invokers[0]["address"]
    else:
        print(f"We found {len(invokers)} deployed invokers.")
        sorted_invokers = sorted(invokers, key=lambda d: d["timestamp"], reverse=True)
        print(f"Returning the most recently deployed invoker ({sorted_invokers[0]['address']})")
        return sorted_invokers[0]["address"]


def get_pausers(invoker):
    global block_number
    # TODO: Will need to iterate over blocks once this method hits block limit
    web3c = brownie.web3.eth.contract(address=invoker.address, abi=invoker.abi)
    event_filter = web3c.events.RoleGranted.createFilter(fromBlock=block_number)
    result = event_filter.get_all_entries()
    pausers = []
    for log in result:
        role = brownie.web3.toHex(log["args"]["role"])
        if role == "0x" + ROLE_PAUSER:
            pauser = log["args"]["account"]
            pausers.append(pauser)
    print(f"The following accounts are able to pause/unpause: {pausers}")
    return pausers


def get_signer():
    print(f"Available accounts: {accounts.load()}")
    account = accounts.load(input("Select account to sign with: "))
    print(f"Signing with {account}")
    return account


def pause(invoker, chain):
    get_pausers(invoker)
    signer = get_signer()
    invoker.pause(get_opts(signer, chain))


def unpause(invoker, chain):
    get_pausers(invoker)
    signer = get_signer()
    invoker.unpause(get_opts(signer, chain))


def main():
    (chain, mode) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    print(
        f"Currently connected to network: '{chain['id']}' network (Chain ID: {chain['chain_id']})"
        f" with mode '{mode}'."
    )

    invoker_address = get_invoker_chainid(chain["chain_id"])

    if invoker_address is None:
        sys.exit(1)

    invoker = Contract.from_abi("Invoker", invoker_address, Invoker.abi)

    is_paused = invoker.paused()
    print("Invoker is paused." if is_paused else "Invoker is not paused.")

    print("Actions available: 'pause', 'unpause', 'quit'")

    try:
        while True:
            val = input("Command: ")
            if val in ["quit", "q"]:
                sys.exit(0)
            elif val == "pause":
                pause(invoker, chain)
            elif val == "unpause":
                unpause(invoker.chain)
            else:
                print(f"Unrecognised command: {val}")
    except KeyboardInterrupt:
        print("")
        print("Quitting gracefully..")
        pass
    except EOFError:
        print("Quitting gracefully..")
        pass
