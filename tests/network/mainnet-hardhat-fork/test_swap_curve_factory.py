import os
from dataclasses import dataclass
from itertools import permutations
from typing import List, Optional

import pytest
import yaml
from brownie import ETH_ADDRESS, interface

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


def pytest_generate_tests(metafunc):
    if "coins" in metafunc.fixturenames:
        metafunc.parametrize(
            "pool,coins",
            [
                (curve_pool, coin)
                for curve_pool in CURVE_POOLS
                for coin in list(permutations(range(len(curve_pool.coins)), 2))
            ],
            indirect=["pool"],
            ids=[
                f"{pool.name}-{coin}"
                for pool in CURVE_POOLS
                for coin in list(permutations(range(len(pool.coins)), 2))
            ],
        )


@pytest.fixture
def pool(request):
    yield request.param


def test_curve_sell(coins, pool, alice, invoker, cswap_curve):

    i, j = coins
    is_underlying = False
    is_crypto = pool.is_crypto

    amount = mint_tokens_for(pool.coins[i], invoker)
    token_in = pool.coins[i]
    token_out = pool.coins[j]

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, 0, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    if token_out == ETH_ADDRESS.lower():
        assert invoker.balance() > 0
    else:
        assert interface.ERC20Detailed(token_out).balanceOf(invoker) > 0


@pytest.mark.parametrize(
    "pool", CURVE_UNDERLYING_POOLS, ids=[c.name for c in CURVE_UNDERLYING_POOLS]
)
def test_curve_sell_underlying(pool: CurvePool, alice, invoker, cswap_curve):

    amount = mint_tokens_for(pool.underlying_coins[0], invoker)

    i = 0
    j = 1
    is_underlying = True
    is_crypto = pool.is_crypto

    token_in = pool.underlying_coins[0]
    token_out = pool.underlying_coins[1]

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, 0, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    if token_out == ETH_ADDRESS.lower():
        assert invoker.balance() > 0
    else:
        assert interface.ERC20Detailed(token_out).balanceOf(invoker) > 0
