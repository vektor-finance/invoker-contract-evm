from brownie import CMove, CSwap, Invoker, accounts, chain, network
from brownie.network.state import Chain

commands = [CMove, CSwap]
# Roles
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"
# keccak256("APPROVED_COMMAND_IMPLEMENTATION")


def deploy_invoker(deployer):
    print("Deploying invoker")
    invoker = Invoker.deploy({"from": deployer})
    return invoker


def deploy_commands(deployer, invoker):
    for command in commands:
        print(f"Deploying {command}")
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
