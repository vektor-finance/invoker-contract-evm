import os
from dataclasses import dataclass
from typing import List, Optional

import pytest
import yaml
from brownie import interface

from data.test_helpers import mint_tokens_for


def test_mint(token, alice):
    amount = mint_tokens_for(token, alice)
    assert token.balanceOf(alice) == amount


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
def test_mint_curve_tokens(pool, alice):
    for coin in pool.coins:
        amount = mint_tokens_for(coin, alice)
        if coin == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
            assert alice.balance() == amount
        else:
            assert interface.ERC20Detailed(coin).balanceOf(alice) / amount == pytest.approx(
                1, rel=1e-5
            )
