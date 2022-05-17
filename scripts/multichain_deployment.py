import json
import os
from typing import Optional

from brownie import Contract, Invoker, MasterDeployer, network
from tabulate import tabulate

from data.chain import get_chain_id

desired_networks = ["mainnet-hardhat-fork", "ethereum-rinkeby-test"]

desired_contracts = [MasterDeployer, Invoker]

RED_CROSS = "\u274c"
GREEN_TICK = "\u2705"


def switch_to(new_network: str) -> None:
    if network.show_active() == new_network:
        return
    network.disconnect()
    network.connect(new_network)


def _ensure_dir(dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def get_master_deployer() -> Optional[Contract]:
    chain_id = get_chain_id()
    _ensure_dir("deployments")
    try:
        with open("deployments/master_deployment.json", "r") as infile:
            master_deployer_contracts = json.load(infile)
    except FileNotFoundError:
        return None

    try:
        return Contract.from_abi(
            f"Master Deployer [{chain_id}]",
            master_deployer_contracts[str(chain_id)]["address"],
            MasterDeployer.abi,
        )
    except KeyError:
        return None


def main():

    deployments = []

    for network_id in desired_networks:
        switch_to(network_id)
        md = get_master_deployer()
        print(md)
        deployments.append([network_id, RED_CROSS, GREEN_TICK])

    headers = [x._name for x in desired_contracts]

    print(tabulate(deployments, headers=["Network", *headers]))


"""
    print(f"Available accounts: {accounts.load()}")
    deployer = accounts.load(input("Which account to deploy from: "))
"""
