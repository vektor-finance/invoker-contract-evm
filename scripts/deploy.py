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
# In the future, we could deploy/mint ether/erc20 tokens for users


import time

from brownie import CMove, CSwap, Invoker, accounts, network

from data.chain import get_chain_from_network_name, get_uni_router_address, get_weth_address

commands = [CMove, CSwap]
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


def get_deployer_opts(deployer, chain):
    if chain.get("eip1559"):
        return {"from": deployer, "priority_fee": "2 gwei"}
    else:
        return {"from": deployer}


def deploy_invoker(deployer, chain):
    print("Deploying invoker")
    invoker = Invoker.deploy(get_deployer_opts(deployer, chain))
    return invoker


def deploy_commands(deployer, invoker, chain):
    WETH_ADDRESS = get_weth_address(chain)
    UNI_ROUTER_ADDRESS = get_uni_router_address(chain)

    for command in commands:
        print(f"==Deploying {command._name}==")
        if command is CSwap:
            deployed_command = command.deploy(
                WETH_ADDRESS,
                UNI_ROUTER_ADDRESS,
                get_deployer_opts(deployer, chain),
            )
        else:
            deployed_command = command.deploy(get_deployer_opts(deployer, chain))
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

    invoker = deploy_invoker(deployer, chain)
    deploy_commands(deployer, invoker, chain)

    print(f"Gas used for deployment: {deployer.gas_used-start_gas} gwei\n")
