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
    venue: str
    chain_id: str
    coins: List[str]
    underlying_coins: Optional[List[str]]
    is_underlying: bool
    is_factory: bool
    is_meta: bool
    is_crypto: bool
    name: str
    pool_address: str
    lp_token: str
    zap_address: Optional[str]
    fee: str
    balance_abi: str

    def __key(self):
        return (self.name, self.pool_address)

    def __hash__(self) -> int:
        return hash(self.__key())


def get_curve_pools(chain_id: str):
    with open(os.path.join("data", "curve.yaml"), "r") as infile:
        _input = yaml.safe_load(infile)

    try:
        curve_pools = [CurvePool(**_data) for _data in _input["curve"][str(chain_id)]]
        return curve_pools
    except KeyError:
        return []
