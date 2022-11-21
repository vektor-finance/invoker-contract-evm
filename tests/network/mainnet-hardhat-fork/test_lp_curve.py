from enum import IntEnum

import pytest
from brownie import ZERO_ADDRESS, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain_id
from data.curve import CurvePool, get_curve_pools
from data.test_helpers import mint_tokens_for


def pytest_generate_tests(metafunc):
    chain_id = get_chain_id()
    pools = get_curve_pools(chain_id)

    if "pool" in metafunc.fixturenames:
        metafunc.parametrize("pool", pools, ids=[pool.name for pool in pools])

    if "metapool" in metafunc.fixturenames:
        metafunc.parametrize(
            "metapool", [p for p in pools if p.is_meta], ids=[p.name for p in pools if p.is_meta]
        )


class CurveLPType(IntEnum):
    BASE = 0
    UNDERLYING = 1
    HELPER = 2
    METAPOOL_HELPER = 3


@pytest.fixture(scope="module")
def clp_curve(invoker, deployer, CLPCurve):
    contract = deployer.deploy(CLPCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract


def get_deposit_params(pool: CurvePool, underlying=False):
    lp_type = CurveLPType.BASE
    deposit_address = pool.pool_address
    metapool_address = ZERO_ADDRESS
    if underlying:
        if pool.zap_address and pool.is_factory and pool.is_meta:
            lp_type = CurveLPType.METAPOOL_HELPER
            deposit_address = pool.zap_address
            metapool_address = pool.pool_address
        elif pool.zap_address:
            lp_type = CurveLPType.HELPER
            deposit_address = pool.zap_address
        else:
            lp_type = CurveLPType.UNDERLYING
    return [0, lp_type, deposit_address, metapool_address]


def get_withdraw_params(pool: CurvePool, underlying=False):
    wip = get_deposit_params(pool, underlying)
    wip[0] = [0] * len(pool.coins)
    return wip


def test_deposit_and_withdraw(pool: CurvePool, invoker, clp_curve, alice):
    amounts = []
    for coin in pool.coins:
        amount = mint_tokens_for(coin, invoker)
        amounts.append(amount / 10)

    deposit = clp_curve.deposit.encode_input(pool.coins, amounts, get_deposit_params(pool, False))
    invoker.invoke([clp_curve], [deposit], {"from": alice})

    withdraw_amount = int(interface.ERC20Detailed(pool.lp_token).balanceOf(invoker) / 2)

    withdraw = clp_curve.withdraw.encode_input(
        pool.lp_token, withdraw_amount, get_withdraw_params(pool, False)
    )
    invoker.invoke([clp_curve], [withdraw], {"from": alice})


def test_metapool_deposit_and_withdraw(metapool: CurvePool, invoker, clp_curve, alice):
    amounts = []
    for coin in metapool.underlying_coins:
        amount = mint_tokens_for(coin, invoker)
        amounts.append(amount / 10)

    deposit = clp_curve.deposit.encode_input(
        metapool.underlying_coins, amounts, get_deposit_params(metapool, True)
    )
    invoker.invoke([clp_curve], [deposit], {"from": alice})

    withdraw_amount = int(interface.ERC20Detailed(metapool.lp_token).balanceOf(invoker) / 2)

    withdraw = clp_curve.withdraw.encode_input(
        metapool.lp_token, withdraw_amount, get_withdraw_params(metapool, False)
    )
    invoker.invoke([clp_curve], [withdraw], {"from": alice})
