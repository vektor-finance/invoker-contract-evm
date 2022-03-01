import json
import os
from dataclasses import dataclass
from typing import List

CURVE_ASSET_TYPE_USD = 0
CURVE_ASSET_TYPE_BTC = 1
CURVE_ASSET_TYPE_ETH = 2
CURVE_ASSET_TYPE_STABLE = 3
CURVE_ASSET_TYPE_CRYPTO = 4


@dataclass
class CurvePool:
    name: str
    swap_address: str
    asset_type: int
    coins: List[str]


def get_curve_pools(chain_id: str):
    chain_id = str(chain_id)
    with open(os.path.join("data", "curve.json"), "r") as infile:
        CURVE_POOLS = json.load(infile)
    obj = CURVE_POOLS.get(chain_id)
    return [CurvePool(**o) for o in obj]
