import brownie

from scripts.deployment import REGISTRY_DEPLOYER, TRUSTED_DEPLOYER, DeployRegistryContainer


def main():
    registry_deployer = brownie.accounts.at(REGISTRY_DEPLOYER)
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER)

    DeployRegistryContainer(registry_deployer, trusted_deployer)
