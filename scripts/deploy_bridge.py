import os
import time

from brownie import ZERO_ADDRESS, CBridge, Invoker, accounts, network

from data.access_control import APPROVED_COMMAND
from data.anyswap import get_anyswap_tokens_for_chain
from data.chain import get_chain_from_network_name, get_wnative_address

OUTPUTS_DEPLOYMENT_DIR = "deployments"


def get_deployer_opts(deployer, chain):
    gas_override = os.environ.get("GAS_GWEI")
    if gas_override:
        return {"from": deployer, "gas_price": f"{gas_override} gwei"}
    if chain.get("eip1559"):
        return {"from": deployer, "priority_fee": "2 gwei"}
    else:
        return {"from": deployer}


def deploy_invoker(deployer, chain):
    print("Deploying invoker")
    invoker = Invoker.deploy(get_deployer_opts(deployer, chain))
    return invoker


def get_any_address(chain, wnative):
    anyswap_tokens = get_anyswap_tokens_for_chain(chain)
    any_native_tokens = [
        token["anyAddress"] for token in anyswap_tokens if token["underlyingAddress"] == wnative
    ]
    try:
        any_native_token = any_native_tokens[0]
    except IndexError:
        any_native_token = ZERO_ADDRESS
    return any_native_token


def deploy_bridge(deployer, invoker, chain):
    WETH_ADDRESS = get_wnative_address(chain)
    ANY_ADDRESS = get_any_address(chain, WETH_ADDRESS)

    print("==Deploying CBridge==")
    if ANY_ADDRESS == ZERO_ADDRESS:
        print(f"Note: it is not possible to bridge native asset on {chain['name']}")

    deployed_address = CBridge.deploy(WETH_ADDRESS, ANY_ADDRESS, get_deployer_opts(deployer, chain))
    invoker.grantRole(
        APPROVED_COMMAND, deployed_address.address, get_deployer_opts(deployer, chain)
    )
    print("Deployed CBridge and authorised contract to be used in invoker")
    time.sleep(1)


def main():
    (chain, mode) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    print(
        f"Deployment network: '{chain['id']}' network (Chain ID: {chain['chain_id']})"
        f" with mode '{mode}'."
    )

    if mode == "fork":
        deployer = accounts[0]
    else:
        print(f"Available accounts: {accounts.load()}")
        deployer = accounts.load(input("Which account to deploy from: "))

    print(f"Deployment user: {deployer}")

    invoker = deploy_invoker(deployer, chain)
    deploy_bridge(deployer, invoker, chain)
