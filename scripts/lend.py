import brownie
from brownie import CLendAave, Invoker, accounts, web3


def main():
    invoker = Invoker.at("0xab7ce6C76E985792f80339183327C3F7A0B78E57")
    deployer = accounts.at("0x0fbc5562670d73b060c44bb6085d39aa628624be", True)
    deployed_contract = deployer.deploy(CLendAave)
    from data.access_control import APPROVED_COMMAND

    invoker.grantRole(APPROVED_COMMAND, deployed_contract, {"from": deployer})

    web3.provider.make_request("evm_setIntervalMining", [5000])
    print(f"User: {brownie.accounts[0]}")

    print(f"Deployed CLendAave: {deployed_contract}")

    # for block in chain.new_blocks():
    #     print(f"Block: {block['number']}")
    #     if len(block["transactions"]) > 0:
    #         print(f"Transactions: {block['transactions']}")
