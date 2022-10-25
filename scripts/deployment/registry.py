import brownie

from scripts.deployment import REGISTRY_USER, TRUSTED_DEPLOYER, DeployRegistryContainer


def main():
    registry_deployer = brownie.accounts.load(REGISTRY_USER)
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    DeployRegistryContainer(registry_deployer, trusted_deployer)
