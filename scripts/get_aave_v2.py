import json
import os

from brownie import interface

AAVE_V2_LENDING_POOL = "0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F"
AAVE_V2_DATA_PROVIDER = "0xa3e42d11d8CC148160CC3ACED757FB44696a9CcA"


def main():
    data = {}
    data["proto"] = []

    LENDING_POOL = interface.AaveV2LendingPool(AAVE_V2_LENDING_POOL)
    ADP = interface.AaveV2DataProvider(AAVE_V2_DATA_PROVIDER)
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
