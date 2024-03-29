from enum import IntEnum

import pytest
from brownie.exceptions import VirtualMachineError

from data.aave.tokens import AaveAssetInfo, get_aave_tokens
from data.chain import get_chain, get_chain_id, get_chain_token, is_venue_on_chain
from data.test_helpers import mint_tokens_for


class InterestRateMode(IntEnum):
    STABLE = 1
    VARIABLE = 2

    @staticmethod
    def list():
        return list(map(lambda c: c.value, InterestRateMode))

    @staticmethod
    def keys():
        return list(map(lambda c: "RATE_" + c.name, InterestRateMode))


@pytest.fixture
def data_provider(Contract, interface):
    yield Contract.from_abi(
        "Aave Data Provider",
        "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d",
        interface.AaveV3DataProvider.abi,
    )


def assert_approx(a, b):
    # equivalent to assert b == a +- 1
    assert a - 1 <= b <= a + 1


def pytest_generate_tests(metafunc):
    chain = get_chain()
    chain_id = str(get_chain_id())
    aave_tokens = get_aave_tokens(chain_id, "3")

    if "aave_token" in metafunc.fixturenames:
        metafunc.parametrize("aave_token", aave_tokens, ids=[a.symbol for a in aave_tokens])

    if "pool" in metafunc.fixturenames:
        pool = is_venue_on_chain("aave_v3", chain)
        if pool:
            metafunc.parametrize("pool", [pool], ids=["Aave V3"])
        else:
            pytest.skip(f"Aave V3 not on network {chain_id}")


def test_supply(clend_aave, pool, aave_token: AaveAssetInfo, invoker, alice, interface):
    token = aave_token.address
    atoken = interface.AaveV2Token(aave_token.aTokenAddress)
    amount = 10**aave_token.decimals

    mint_tokens_for(token, invoker, amount)

    calldata_supply = clend_aave.supply.encode_input(pool, token, amount, alice)

    invoker.invoke([clend_aave], [calldata_supply], {"from": alice})
    assert_approx(atoken.balanceOf(alice), amount)


def test_withdraw(clend_aave, pool, invoker, aave_token: AaveAssetInfo, alice, interface):
    token = interface.ERC20Detailed(aave_token.address)
    atoken = aave_token.aTokenAddress
    amount = 10**aave_token.decimals

    mint_tokens_for(atoken, invoker, amount)

    calldata_withdraw = clend_aave.withdraw.encode_input(pool, atoken, amount, alice)
    invoker.invoke([clend_aave], [calldata_withdraw], {"from": alice})

    assert_approx(token.balanceOf(alice), amount)


def test_withdraw_all(clend_aave, pool, invoker, aave_token: AaveAssetInfo, alice, interface):
    token = interface.ERC20Detailed(aave_token.address)
    atoken = interface.IAaveToken(aave_token.aTokenAddress)
    amount = 10**aave_token.decimals

    interface.ERC20Detailed(atoken).approve(invoker, 2**256 - 1, {"from": alice})
    mint_tokens_for(atoken, alice, amount)

    calldata_withdraw_all = clend_aave.withdrawAllUser.encode_input(pool, atoken, alice)
    invoker.invoke([clend_aave], [calldata_withdraw_all], {"from": alice})

    assert token.balanceOf(alice) >= amount - 1
    assert token.balanceOf(invoker) == 0
    assert atoken.balanceOf(invoker) == 0


@pytest.mark.parametrize("mode", InterestRateMode.list(), ids=InterestRateMode.keys())
def test_borrow_and_repay(
    clend_aave, pool, cmove, invoker, aave_token: AaveAssetInfo, alice, mode, interface
):
    token = interface.ERC20Detailed(aave_token.address)
    vdebt = interface.AaveV2DebtToken(aave_token.variableDebtTokenAddress)
    sdebt = interface.AaveV2DebtToken(aave_token.stableDebtTokenAddress)
    amount = 10**aave_token.decimals

    # use USDC for collateral, except to borrow usdc - then use wbtc
    collateral = (
        get_chain_token("wbtc")["address"]
        if aave_token.symbol == "USDC"
        else get_chain_token("usdc")["address"]
    )
    mint_tokens_for(collateral, invoker, 1e12)

    calldata_supply = clend_aave.supply.encode_input(pool, collateral, 1e12, alice)

    invoker.invoke([clend_aave], [calldata_supply], {"from": alice})

    if mode == InterestRateMode.STABLE:
        sdebt.approveDelegation(invoker, 2**256 - 1, {"from": alice})
    elif mode == InterestRateMode.VARIABLE:
        vdebt.approveDelegation(invoker, 2**256 - 1, {"from": alice})

    calldata_borrow = clend_aave.borrow.encode_input(pool, token, amount / 10, mode)
    calldata_move_out = cmove.moveAllERC20Out.encode_input(token, alice)
    try:
        invoker.invoke([clend_aave, cmove], [calldata_borrow, calldata_move_out], {"from": alice})
    except VirtualMachineError as e:
        if e.revert_msg in ["30", "31"]:
            # 30: "Borrowing not enabled"
            # 31: "Stable borrowing not enabled"
            return
        else:
            raise e from None

    assert_approx(token.balanceOf(alice), amount / 10)

    calldata_repay = clend_aave.repay.encode_input(pool, token, amount / 10, mode)
    token.transfer(invoker, amount / 10, {"from": alice})
    invoker.invoke([clend_aave], [calldata_repay], {"from": alice})
    assert_approx(token.balanceOf(alice), 0)
