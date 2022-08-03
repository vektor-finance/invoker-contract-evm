import json
import os

from brownie import interface


def main():
    data = {}
    data["proto"] = []

    LENDING_POOL = interface.AaveV2LendingPool("0x8dff5e27ea6b7ac08ebfdf9eb090f32ee9a30fcf")
    ADP = interface.AaveV2DataProvider("0x7551b5D2763519d4e37e8B81929D336De671d46d")
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
            variable_debt_address,
            stable_debt_address,
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
