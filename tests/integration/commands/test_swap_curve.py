import atexit
from itertools import permutations

import brownie
import pytest
from brownie import ETH_ADDRESS, interface
from brownie.exceptions import VirtualMachineError

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_id
from data.curve import CurvePool, get_curve_pools
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def cswap_curve(invoker, deployer, CSwapCurve):

    contract = deployer.deploy(CSwapCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def pytest_generate_tests(metafunc):
    chain_id = get_chain_id()
    pools = get_curve_pools(chain_id)
    underlying_pools = [p for p in pools if p.is_underlying]

    if "coins" in metafunc.fixturenames:
        metafunc.parametrize(
            "pool, coins",
            [
                (curve_pool, coin)
                for curve_pool in pools
                for coin in list(permutations(range(len(curve_pool.coins)), 2))
            ],
            ids=[
                f"{pool.name}-{coin}"
                for pool in pools
                for coin in list(permutations(range(len(pool.coins)), 2))
            ],
        )
    if "underlying_coins" in metafunc.fixturenames:
        metafunc.parametrize(
            "pool, underlying_coins",
            [
                (curve_pool, coin)
                for curve_pool in underlying_pools
                for coin in list(permutations(range(len(curve_pool.coins)), 2))
            ],
            ids=[
                f"{pool.name}-{coin}"
                for pool in underlying_pools
                for coin in list(permutations(range(len(pool.coins)), 2))
            ],
        )


def quote_output(pool: CurvePool, i, j, value, underlying=False):
    contract = None
    if pool.is_crypto:
        contract = interface.CurveCryptoPool(pool.pool_address)
    else:
        contract = interface.CurvePool(pool.pool_address)

    try:
        if underlying:
            return contract.get_dy_underlying(i, j, value)
        else:
            return contract.get_dy(i, j, value)
    except (VirtualMachineError, ValueError):
        atexit.register(print, f"Could not get quote for {pool.name} {pool.pool_address}")


DEFAULT_SLIPPAGE = 0.99


def test_curve_sell(coins, pool: CurvePool, alice, invoker, cswap_curve):

    i, j = coins
    is_underlying = False
    is_crypto = pool.is_crypto

    amount = mint_tokens_for(pool.coins[i], invoker)
    token_in = pool.coins[i]
    token_out = pool.coins[j]

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    expected_output = quote_output(pool, i, j, amount, is_underlying)
    min_output = int(expected_output * DEFAULT_SLIPPAGE)

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, min_output, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    if token_out == ETH_ADDRESS.lower():
        assert invoker.balance() > min_output
    else:
        assert interface.ERC20Detailed(token_out).balanceOf(invoker) > min_output


def test_curve_sell_underlying(underlying_coins, pool: CurvePool, alice, invoker, cswap_curve):

    i, j = underlying_coins
    is_underlying = True
    is_crypto = pool.is_crypto

    amount = mint_tokens_for(pool.underlying_coins[i], invoker)
    token_in = pool.underlying_coins[i]
    token_out = pool.underlying_coins[j]

    params = [pool.pool_address, i, j, (is_crypto * 2 + is_underlying)]

    expected_output = quote_output(pool, i, j, amount, is_underlying)
    min_output = int(expected_output * DEFAULT_SLIPPAGE)

    calldata_swap = cswap_curve.sell.encode_input(amount, token_in, token_out, min_output, params)

    invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})

    if token_out == ETH_ADDRESS.lower():
        assert invoker.balance() > min_output
    else:
        assert interface.ERC20Detailed(token_out).balanceOf(invoker) > min_output


def test_curve_buy_fail(invoker, cswap_curve, alice):
    chain_id = get_chain_id()
    curve_pools = get_curve_pools(chain_id)
    try:
        pool = curve_pools[0]
    except IndexError:
        pytest.skip("No curve pools to test")

    amount = mint_tokens_for(pool.coins[0], invoker)
    token_in = pool.coins[0]
    token_out = pool.coins[1]
    is_crypto = pool.is_crypto

    params = [pool.pool_address, 0, 1, is_crypto * 2]

    calldata_swap = cswap_curve.buy.encode_input(amount, token_in, token_out, 0, params)

    with brownie.reverts("CSwapCurve:buy not supported"):
        invoker.invoke([cswap_curve], [calldata_swap], {"from": alice})
