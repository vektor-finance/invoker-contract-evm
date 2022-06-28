import os
from dataclasses import dataclass
from typing import List, Optional

import pytest
import yaml
from brownie import interface

from data.access_control import APPROVED_COMMAND
from data.test_helpers import mint_tokens_for


@dataclass
class CurvePool:
    name: str
    pool_address: str
    coins: List[str]
    is_underlying: bool
    underlying_coins: Optional[List[str]] = None
    is_v1: Optional[bool] = False
    is_crypto: Optional[bool] = False


with open(os.path.join("data", "curve_mainnet.yaml"), "r") as infile:
    _input = yaml.safe_load(infile)
    CURVE_POOLS = [CurvePool(**_data) for _data in _input]
    CURVE_UNDERLYING_POOLS = [p for p in CURVE_POOLS if p.is_underlying]


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve):

    contract = deployer.deploy(CSwapCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.mark.parametrize("pool", CURVE_POOLS, ids=[c.name for c in CURVE_POOLS])
def test_curve_sell(pool: CurvePool, alice, invoker, cswap_curve):
    if "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" in pool.coins:
        return

    amount = mint_tokens_for(pool.coins[0], invoker)

    i = 0
    j = 1
    is_underlying = False
    is_crypto = pool.is_crypto

    token_in = interface.ERC20Detailed(pool.coins[0])
    token_out = interface.ERC20Detailed(pool.coins[1])

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, 0, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    assert token_out.balanceOf(invoker) > 0


@pytest.mark.parametrize(
    "pool", CURVE_UNDERLYING_POOLS, ids=[c.name for c in CURVE_UNDERLYING_POOLS]
)
def test_curve_sell_underlying(pool: CurvePool, alice, invoker, cswap_curve):

    if "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" in pool.coins:
        return

    amount = mint_tokens_for(pool.underlying_coins[0], invoker)

    i = 0
    j = 1
    is_underlying = True
    is_crypto = pool.is_crypto

    token_in = interface.ERC20Detailed(pool.underlying_coins[0])
    token_out = interface.ERC20Detailed(pool.underlying_coins[1])

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, 0, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    assert token_out.balanceOf(invoker) > 0
