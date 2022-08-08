import itertools

import pytest
from brownie import interface

from data.chain import get_chain_id
from data.curve import get_curve_pools
from data.test_helpers import mint_tokens_for


def test_mint(token, alice):
    amount = mint_tokens_for(token, alice)
    assert token.balanceOf(alice) == amount


def pytest_generate_tests(metafunc):
    chain_id = get_chain_id()
    pools = get_curve_pools(chain_id)

    if "coin" in metafunc.fixturenames:
        coins = list(set(itertools.chain(*[pool.coins for pool in pools])))
        metafunc.parametrize(
            "coin",
            coins,
        )

    if "underlying_coin" in metafunc.fixturenames:
        underlying_coins = list(
            set(itertools.chain(*[pool.underlying_coins or [] for pool in pools]))
        )
        metafunc.parametrize("underlying_coin", underlying_coins)


def test_mint_curve_tokens(coin, alice):
    amount = mint_tokens_for(coin, alice)
    if coin == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
        assert alice.balance() == amount
    else:
        assert interface.ERC20Detailed(coin).balanceOf(alice) / amount == pytest.approx(1, rel=1e-5)


def test_mint_underlying_curve_tokens(underlying_coin, alice):
    amount = mint_tokens_for(underlying_coin, alice)
    if underlying_coin == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
        assert alice.balance() == amount
    else:
        assert interface.ERC20Detailed(underlying_coin).balanceOf(alice) / amount == pytest.approx(
            1, rel=1e-5
        )
