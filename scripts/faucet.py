# Faucet - swaps ETH for selection of ERC20s using Uniswap directly

import os
import time

from brownie import Contract, accounts, interface, network
from tabulate import tabulate

from data.chain import get_chain_from_network_name, get_uni_router_address, get_weth_address

ROUTER = interface.IUniswapV2Router02
WETH = interface.IWETH
ERC20Detailed = interface.ERC20Detailed


def get_deployer_opts(account, value, chain):
    if chain.get("eip1559"):
        return {"from": account, "value": value, "priority_fee": "2 gwei"}
    else:
        return {"from": account, "value": value}


# mainnet only
def swap_eth_for_tokens(account, chain, eth_amount=0.5):
    print(f"Swapping tokens for account {account.address}")

    tokens = chain["assets"]

    WETH_ADDRESS = get_weth_address(chain)
    UNI_ROUTER_ADDRESS = get_uni_router_address(chain)

    uni_router = Contract.from_abi("Router", UNI_ROUTER_ADDRESS, ROUTER.abi)
    weth = Contract.from_abi("Weth", WETH_ADDRESS, WETH.abi)
    opts = get_deployer_opts(account, eth_amount * 1e18, chain)

    print(f"Token list: {[tok['name'] for tok in tokens]}")

    balances = []
    for token in tokens:
        address = token["address"]
        if not address:
            continue  # undefined for native asset
        if token.get("wrapped_native"):
            continue  # dont swap into wrapped token
        token = Contract.from_abi("ERC20", address, ERC20Detailed.abi)
        symbol = token.symbol()
        decimals = token.decimals()
        path = [weth.address, token.address]
        min_amount = 0

        print(f"Swapping {eth_amount} ETH for {symbol}")

        uni_router.swapExactETHForTokens(
            min_amount * decimals,
            path,
            account,
            int(time.time()) + 1,
            opts,
        )

        balance = token.balanceOf(account) / (10 ** decimals)
        balances.append([balance, symbol])
        print(f"Swapped {eth_amount} ETH for {balance} {symbol}")

    balances.insert(0, [account.balance() / 1e18, "ETH"])
    print(f"Balances for {account.address}\n")
    print(
        tabulate(
            balances,
            headers=["Balance", "Symbol"],
            floatfmt=",.5f",
            tablefmt="psql",
            numalign="right",
        )
    )


# Allow user to set the account index or force unlock an address
# Defaults to account 0
def get_account():
    account = accounts[0]
    _account = os.getenv("ACCOUNT")
    if _account:
        try:
            index = int(_account)
            account = accounts[index]
        except ValueError:
            account = accounts.at(_account, force=True)
    return account


# Allow user to set the account index or force unlock an address
# Defaults to account 0.5
def get_eth_amount():
    return float(os.getenv("ETH", 0.5))


def main():

    (chain, _) = get_chain_from_network_name(network.show_active())
    if not chain:
        raise ValueError(
            "Network not supported in config. Please review data/chains.yaml", network.show_active()
        )

    print(f"Script running on '{chain['id']}' network (Chain ID: {chain['chain_id']})")
    account = get_account()
    eth_amount = get_eth_amount()
    swap_eth_for_tokens(account, chain, eth_amount)
