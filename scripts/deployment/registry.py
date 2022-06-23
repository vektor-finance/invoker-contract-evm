import brownie

from scripts.deployment import REGISTRY_USER, TRUSTED_DEPLOYER, DeployRegistryContainer


def main():
    registry_deployer = brownie.accounts.load(REGISTRY_USER)
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    brownie.accounts[0].transfer(registry_deployer, 10e18)

    DeployRegistryContainer(registry_deployer, trusted_deployer)
