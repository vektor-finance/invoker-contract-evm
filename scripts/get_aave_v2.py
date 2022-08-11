import json
import os

from brownie import interface


def main():
    data = {}
    data["proto"] = []

    LENDING_POOL = interface.AaveV2LendingPool("0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9")
    ADP = interface.AaveV2DataProvider("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
    reserve_tokens = ADP.getAllReservesTokens()

    for (symbol, token_address) in reserve_tokens:
        (
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            a_token_address,
            stable_debt_address,
            variable_debt_address,
            _,
            _,
        ) = LENDING_POOL.getReserveData(token_address)
        decimals = interface.ERC20Detailed(token_address).decimals()

        data["proto"].append(
            {
                "symbol": symbol,
                "address": token_address,
                "aTokenAddress": a_token_address,
                "aTokenSymbol": "a" + symbol,
                "stableDebtTokenAddress": stable_debt_address,
                "variableDebtTokenAddress": variable_debt_address,
                "decimals": decimals,
            }
        )

    with open(os.path.join("data/aave", "output.json"), "w") as outfile:
        json.dump(data, outfile)
