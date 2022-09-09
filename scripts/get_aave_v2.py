import json
import os

from brownie import interface

AAVE_V2_LENDING_POOL = "0xE29A55A6AEFf5C8B1beedE5bCF2F0Cb3AF8F91f5"
AAVE_V2_DATA_PROVIDER = "0xc9704604E18982007fdEA348e8DDc7CC652E34cA"


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
