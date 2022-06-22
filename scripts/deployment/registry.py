import brownie

from scripts.deployment import REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, DeployRegistryContainer


def main():
    registry_deployer = brownie.accounts.at(
        REGISTRY_DEPLOYER, force=True
    )  # for live, we get user from brownie keystore
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    DeployRegistryContainer(registry_deployer, trusted_deployer)
