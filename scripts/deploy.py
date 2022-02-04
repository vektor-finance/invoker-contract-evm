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


from brownie import CMove, CSwap, Invoker, accounts, chain, network
from scripts.addresses import WETH_ADDRESS, UNI_ROUTER_ADDRESS

commands = [CMove, CSwap]
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


def get_deployer_opts(deployer, chain):
    if chain.id == 1 or chain.id == 4:
        # TODO: Define deployment strategy based on chain.id
        return {"from": deployer, "priority_fee": "2 gwei"}
    else:
        return {"from": deployer}


def deploy_invoker(deployer, chain):
    print("Deploying invoker")
    invoker = Invoker.deploy(get_deployer_opts(deployer, chain))
    return invoker


def get_chain_id():
    # Hardhat network has chain.id 1337
    # When we start forking multiple different networks, we need to map
    return 1 if chain.id == 1337 else chain.id


def deploy_commands(deployer, invoker, chain):
    for command in commands:
        print(f"Deploying {command._name}")
        if command is CSwap:
            deployed_command = command.deploy(
                WETH_ADDRESS[get_chain_id()],
                UNI_ROUTER_ADDRESS[get_chain_id()],
                get_deployer_opts(deployer, chain),
            )
        else:
            deployed_command = command.deploy(get_deployer_opts(deployer, chain))
        invoker.grantRole(
            APPROVED_COMMAND, deployed_command.address, get_deployer_opts(deployer, chain)
        )


def main():
    deployer = accounts[0]

    print(f"Deployment network: '{network.show_active()}' network (Chain ID: {chain.id})")
    print(f"Deployment user: {deployer}")

    invoker = deploy_invoker(deployer, chain)
    deploy_commands(deployer, invoker, chain)

    print(f"Gas used for deployment: {deployer.gas_used} gwei\n")
