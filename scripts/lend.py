from brownie import CLendAaveV2, Invoker, accounts


def main():
    invoker = Invoker.at("0xab7ce6C76E985792f80339183327C3F7A0B78E57")
    deployer = accounts.at("0x0fbc5562670d73b060c44bb6085d39aa628624be", True)
    deployer.deploy(CLendAaveV2, "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9")
    from data.access_control import APPROVED_COMMAND

    invoker.grantRole(
        APPROVED_COMMAND, "0xE2b7CE0aFd03cA11674455FddFd664FdE0705017", {"from": deployer}
    )
