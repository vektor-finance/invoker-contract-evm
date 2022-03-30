# Deployment script to deploy all contracts on hardhat fork
# To run, please type `brownie run deploy` in console
# The script will deploy the invoker contract, and all command contracts
# Appropriate access control will also be initialised
# The script will then continue to mine new blocks until closed
# To connect with metamask (or alternate wallet), create a custom network
# -- network name: Vektor test net
# -- RPC url: http://127.0.0.1:8545
# -- Chain ID: 1337
# The other settings can be left blank


import json
import os
import time

from brownie import (
    CMove,
    CSwapCurve,
    CSwapUniswapV2,
    CSwapUniswapV3,
    CWrap,
    Invoker,
    accounts,
    network,
)

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_from_network_name, get_wnative_address
from data.git import get_git_revision_hash, get_git_revision_short_hash

commands = [CMove, CWrap, CSwapUniswapV2, CSwapUniswapV3, CSwapCurve]

OUTPUTS_DEPLOYMENT_DIR = "deployments"


def log_deployment(contract, chain):
    if not os.path.exists(OUTPUTS_DEPLOYMENT_DIR):
        os.makedirs(OUTPUTS_DEPLOYMENT_DIR)
    try:
        with open(os.path.join(OUTPUTS_DEPLOYMENT_DIR, "deployments.json"), "r") as infile:
            data = json.load(infile)
    except FileNotFoundError:
        data = {}
    chain_id = str(chain.get("chain_id"))
    deployments = data.get(chain_id)
    deployments = [] if deployments is None else deployments
    deployments.append(
        {
            "contract": contract._name,
            "address": contract.address,
            "block_number": contract.tx.block_number,
            "timestamp": int(time.time()),
            "git_sha": get_git_revision_short_hash(),
            "git_sha_long": get_git_revision_hash(),
        }
    )
    data[chain_id] = deployments

    with open(os.path.join(OUTPUTS_DEPLOYMENT_DIR, "deployments.json"), "w") as outfile:
        json.dump(data, outfile)


def get_deployer_opts(deployer, chain):
    gas_override = os.environ.get("GAS_GWEI")
    if gas_override:
        return {"from": deployer, "gas_price": f"{gas_override} gwei"}
    if chain.get("eip1559"):
        return {"from": deployer, "priority_fee": "2 gwei"}
    else:
        return {"from": deployer}


def deploy_invoker(deployer, chain, log=False):
    print("Deploying invoker")
    invoker = Invoker.deploy(get_deployer_opts(deployer, chain))
    if log:
        log_deployment(invoker, chain)
    return invoker


def deploy_commands(deployer, invoker, chain, log=False):
    WETH_ADDRESS = get_wnative_address(chain)

    for command in commands:
        print(f"==Deploying {command._name}==")
        args = []
        if command == CWrap:
            args = [WETH_ADDRESS]
        deployed_command = command.deploy(*args, get_deployer_opts(deployer, chain))
        if log:
            log_deployment(deployed_command, chain)
        invoker.grantRole(
            APPROVED_COMMAND, deployed_command.address, get_deployer_opts(deployer, chain)
        )
        print(f"Deployed {command._name} and authorised contract to be used in invoker")
        time.sleep(1)


def main():
    (chain, mode) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    print(
        f"Deployment network: '{chain['id']}' network (Chain ID: {chain['chain_id']})"
        f" with mode '{mode}'."
    )

    if mode == "fork":
        deployer = accounts[0]
    else:
        print(f"Available accounts: {accounts.load()}")
        deployer = accounts.load(input("Which account to deploy from: "))

    print(f"Deployment user: {deployer}")

    start_gas = deployer.gas_used  # in case somebody has sent tx with deployer

    log = mode == "prod"

    invoker = deploy_invoker(deployer, chain, log=log)
    deploy_commands(deployer, invoker, chain, log=log)

    print(f"Gas used for deployment: {deployer.gas_used-start_gas} gwei\n")
