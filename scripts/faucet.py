# Faucet - swaps ETH for selection of ERC20s using Uniswap directly

import os
import time

from brownie import Contract, accounts, chain, network
from tabulate import tabulate

from scripts.addresses import TOKEN_ADDRESSES, UNI_ROUTER_ADDRESS, WETH_ADDRESS


def get_chain_id(chain):
    if chain.id in [1, 1337]:
        return 1
    else:
        return chain.id


def get_deployer_opts(account, value, chain):
    if chain.id in [1, 1337]:
        return {"from": account, "value": value, "priority_fee": "2 gwei"}
    else:
        return {"from": account, "value": value}


# mainnet only
def swap_eth_for_tokens(account, chain, eth_amount=0.5):
    print(f"Swapping tokens for account {account.address}")
    chain_id = get_chain_id(chain)
    uni_router = Contract.from_explorer(UNI_ROUTER_ADDRESS[chain_id])
    weth = Contract.from_explorer(WETH_ADDRESS[chain_id])
    token_addresses = TOKEN_ADDRESSES[chain_id]

    balances = []
    for address in token_addresses:
        token = Contract.from_explorer(address)
        path = [weth.address, token.address]
        min_amount = 0

        print(f"Swapping {eth_amount} ETH for {token.symbol()}")

        uni_router.swapExactETHForTokens(
            min_amount * token.decimals(),
            path,
            account,
            int(time.time()) + 1,
            {"from": account, "value": eth_amount * 1e18, "priority_fee": "2 gwei"},
        )

        balance = token.balanceOf(account) / (10 ** token.decimals())
        balances.append([balance, token.symbol()])
        print(f"Swapped {eth_amount} ETH for {balance} {token.symbol()}")

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
    print(f"Network: '{network.show_active()}' network (Chain ID: {chain.id})")

    account = get_account()
    eth_amount = get_eth_amount()
    swap_eth_for_tokens(account, chain, eth_amount)
