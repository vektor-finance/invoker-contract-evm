# aave mainnet tokens
# https://aave.github.io/aave-addresses/mainnet.json

import json
import os
from dataclasses import dataclass


@dataclass
class AaveAssetInfo:
    aTokenAddress: str
    aTokenSymbol: str
    stableDebtTokenAddress: str
    variableDebtTokenAddress: str
    symbol: str
    address: str
    decimals: int


def get_aave_tokens(chain_id: str, version: int):
    try:
        file_name = {
            "1": {"2": "mainnet_v2.json"},
            "137": {"2": "polygon_v2.json", "3": "polygon_v3.json"},
        }
        with open(os.path.join("data/aave", file_name[chain_id][version]), "r") as infile:
            input = json.load(infile)
        tokens = [AaveAssetInfo(**data) for data in input["proto"]]
        # KNC is disabled on protocol
        tokens[:] = [t for t in tokens if t.symbol != "KNC"]
        return tokens
    except KeyError:
        return []
