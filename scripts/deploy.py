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
from brownie.network.state import Chain

commands = [CMove, CSwap]
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


weth_address = {
    1: "0xC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",  # Mainnet
    4: "0xc778417E063141139Fce010982780140Aa0cD5Ab",  # Rinkeby
    1337: "0xC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",  # Hardhat fork
    # note regarding fork: if we fork rinkeby rather than mainnet, we need to update address
}


def get_weth_address():
    return weth_address[Chain().id]


def deploy_invoker(deployer):
    print("Deploying invoker")
    invoker = Invoker.deploy({"from": deployer})
    return invoker


def deploy_commands(deployer, invoker):
    for command in commands:
        print(f"Deploying {command}")
        if command is CSwap:
            deployed_command = command.deploy(get_weth_address(), {"from": deployer})
        else:
            deployed_command = command.deploy({"from": deployer})
        invoker.grantRole(APPROVED_COMMAND, deployed_command.address, {"from": deployer})


def deploy_all_contracts():
    deployer = accounts[0]
    print(f"Deployment user: {accounts[0]}")
    invoker = deploy_invoker(deployer)
    deploy_commands(deployer, invoker)


def main():
    print(f"Deploying to '{network.show_active()}' network")
    print(f"Chain ID: {Chain().id}")
    deploy_all_contracts()
    accounts[0].transfer("0xc7711f36b2C13E00821fFD9EC54B04A60AEfbd1b", "1 ether")
    for block in chain.new_blocks():
        print(f"Mining block {block.number}")
