import time

import brownie
from brownie import Invoker

from scripts.deployment import TRUSTED_USER


def main():
    trusted_deployer = brownie.accounts.load(TRUSTED_USER)
    # This address is hardcoded to the instance we deployed in August 2022
    # It was updated on 2022-11-2
    invoker = Invoker.at("0xA7dAC6938b17c4ac0BF879F4Bf8d2020c2c1EdB1")
    invoker.pause({"from": trusted_deployer})
    print(f"Successfully paused/disabled invoker on {brownie.network.show_active()}")
    time.sleep(1)
