import json
import os
import sys

from brownie import Contract, Invoker, network

from data.chain import get_chain_from_network_name
from data.utils import get_opts, get_signer


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


def pause(invoker, chain):
    signer = get_signer()
    invoker.pause(get_opts(signer, chain))


def unpause(invoker, chain):
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
    )

    if mode != "prod":
        raise ValueError(f"Cannot run script in {mode} environment.")

    invoker_address = get_invoker_chainid(chain["chain_id"])

    if not invoker_address:
        raise ValueError(f"Could not find deployed invoker on network {chain['id']}")

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
                unpause(invoker, chain)
            else:
                print(f"Unrecognised command: {val}")
    except (KeyboardInterrupt, EOFError):
        print("Quitting gracefully..")
