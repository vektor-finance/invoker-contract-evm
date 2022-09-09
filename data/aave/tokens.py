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
    venue: str
    pool: str


file_name = {
    "1": {"2": "mainnet_v2.json"},
    "137": {"2": "polygon_v2.json", "3": "polygon_v3.json"},
    "42161": {"2": "radiant.json"},
    "250": {"2": ["geist.json", "granary_fantom.json"]},
    # "43114": {"2": "granary_avalanche.json"},
    "10": {"2": "granary_optimism.json"},
}


def get_aave_tokens(chain_id: str, version: int):
    tokens = []
    try:
        files = file_name[chain_id][version]
        if isinstance(files, str):
            files = [files]
        for file in files:
            with open(os.path.join("data/aave", file), "r") as infile:
                input = json.load(infile)
            _tokens = [
                AaveAssetInfo(**data, venue=file.split(".")[0], pool=input["pool"])
                for data in input["proto"]
            ]
            tokens.extend(_tokens)
        return tokens
    except KeyError:
        return []
