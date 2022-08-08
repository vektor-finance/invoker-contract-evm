import brownie
from brownie import CLendAave, Invoker, accounts, web3


def main():
    invoker = Invoker.at("0xab7ce6C76E985792f80339183327C3F7A0B78E57")
    deployer = accounts.at("0x0fbc5562670d73b060c44bb6085d39aa628624be", True)
    deployer.deploy(CLendAave, "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9")
    from data.access_control import APPROVED_COMMAND

    invoker.grantRole(
        APPROVED_COMMAND, "0xE2b7CE0aFd03cA11674455FddFd664FdE0705017", {"from": deployer}
    )

    web3.provider.make_request("evm_setIntervalMining", [5000])
    print(brownie.accounts[0])

    # for block in chain.new_blocks():
    #     print(f"Block: {block['number']}")
    #     if len(block["transactions"]) > 0:
    #         print(f"Transactions: {block['transactions']}")
