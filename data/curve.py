import json
import os
from dataclasses import dataclass
from enum import IntEnum
from typing import List


class CurveAssetType(IntEnum):
    """CurveAssetType is required to be IntEnum to allow comparison with integers
    https://docs.python.org/3/library/enum.html#intenum
    """

    USD = 0
    BTC = 1
    ETH = 2
    STABLE = 3
    CRYPTO = 4


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
    if obj is not None:
        return [CurvePool(**o) for o in obj]
