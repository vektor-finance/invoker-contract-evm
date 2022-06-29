import os
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

import yaml


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
    pool_address: str
    coins: List[str]
    is_underlying: bool
    underlying_coins: Optional[List[str]] = None
    is_v1: Optional[bool] = False
    is_crypto: Optional[bool] = False

    def __key(self):
        return (self.name, self.pool_address)

    def __hash__(self) -> int:
        return hash(self.__key())


def get_curve_pools(chain_id: str):
    with open(os.path.join("data", "curve.yaml"), "r") as infile:
        _input = yaml.safe_load(infile)

    curve_pools = [CurvePool(**_data) for _data in _input[str(chain_id)]]

    return curve_pools
