# aave mainnet tokens
# https://aave.github.io/aave-addresses/mainnet.json

import json
import os
from dataclasses import dataclass


@dataclass
class AaveToken:
    aTokenAddress: str
    aTokenSymbol: str
    stableDebtTokenAddress: str
    variableDebtTokenAddress: str
    symbol: str
    address: str
    decimals: int


def get_aave_tokens(chain_id: str):
    if chain_id == "1":
        with open(os.path.join("data/aave", "mainnet.json"), "r") as infile:
            input = json.load(infile)
        tokens = [AaveToken(**data) for data in input["proto"]]
        # KNC is disabled on protocol
        tokens[:] = [t for t in tokens if t.symbol != "KNC"]
        return tokens
