import json
import os

from brownie import interface

AAVE_V2_LENDING_POOL = "0x5E15d5E33d318dCEd84Bfe3F4EACe07909bE6d9c"
AAVE_V2_DATA_PROVIDER = "0x24dCbd376Db23e4771375092344f5CbEA3541FC0"


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
