import json
import os

from brownie import interface


def main():
    data = {}
    data["proto"] = []

    ADP = interface.AaveV3DataProvider("0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3")
    reserve_tokens = ADP.getAllReservesTokens()

    for (symbol, token_address) in reserve_tokens:
        (
            a_token_address,
            stable_debt_address,
            variable_debt_address,
        ) = ADP.getReserveTokensAddresses(token_address)
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
