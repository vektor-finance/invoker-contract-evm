import json
import os

from brownie import interface

AAVE_V2_LENDING_POOL = "0x7220FFD5Dc173BA3717E47033a01d870f06E5284"
AAVE_V2_DATA_PROVIDER = "0x3132870d08f736505FF13B19199be17629085072"


def main():
    data = {}
    data["pool"] = AAVE_V2_LENDING_POOL
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
        asymbol = interface.ERC20Detailed(a_token_address).symbol()

        data["proto"].append(
            {
                "symbol": symbol,
                "address": token_address,
                "aTokenAddress": a_token_address,
                "aTokenSymbol": asymbol,
                "stableDebtTokenAddress": stable_debt_address,
                "variableDebtTokenAddress": variable_debt_address,
                "decimals": decimals,
            }
        )

    with open(os.path.join("data/aave", "output.json"), "w") as outfile:
        json.dump(data, outfile)
