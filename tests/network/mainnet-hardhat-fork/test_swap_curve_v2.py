import os
from dataclasses import dataclass
from typing import List, Optional

import pytest
import yaml

from data.test_helpers import mint_tokens_for


@dataclass
class CurvePool:
    name: str
    pool_address: str
    coins: List[str]
    is_underlying: bool
    underlying_coins: Optional[List[str]] = None
    is_v1: Optional[bool] = False


with open(os.path.join("data", "curve_mainnet.yaml"), "r") as infile:
    _input = yaml.safe_load(infile)
    CURVE_POOLS = [CurvePool(**_data) for _data in _input]


@pytest.mark.parametrize("pool", CURVE_POOLS, ids=[c.name for c in CURVE_POOLS])
def test_sell(pool: CurvePool, alice, invoker):
    for coin in pool.coins:
        mint_tokens_for(coin, alice)
