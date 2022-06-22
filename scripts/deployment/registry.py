import brownie

from scripts.deployment import DeployRegistryContainer

REGISTRY_DEPLOYER = "0x12331c2dDb0E841a40Bd5239365CE98F4b114e87"  # hardcoded
TRUSTED_DEPLOYER = "0xbeEf6e409E5374c15C50f60D07098aF846cB8178"  # hardcoded


def main():
    registry_deployer = brownie.accounts.at(
        REGISTRY_DEPLOYER, force=True
    )  # for live, we get user from brownie keystore
    trusted_deployer = brownie.accounts.at(TRUSTED_DEPLOYER, force=True)

    DeployRegistryContainer(registry_deployer, trusted_deployer)
