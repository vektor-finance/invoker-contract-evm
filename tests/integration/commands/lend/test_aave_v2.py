from enum import IntEnum

import pytest
from brownie.exceptions import VirtualMachineError

from data.aave.tokens import AaveAssetInfo, get_aave_tokens
from data.chain import get_chain_id, get_chain_token
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
        interface.AaveDataProvider.abi,
    )


def assert_approx(a, b):
    # equivalent to assert b == a +- 2
    assert a - 2 <= b <= a + 2


def pytest_generate_tests(metafunc):
    chain_id = str(get_chain_id())
    aave_tokens = get_aave_tokens(chain_id, "2")

    if "aave_token" in metafunc.fixturenames:
        metafunc.parametrize(
            "aave_token", aave_tokens, ids=[f"{a.venue}-{a.symbol}" for a in aave_tokens]
        )


def test_supply(clend_aave, aave_token: AaveAssetInfo, invoker, alice, interface):
    if aave_token.symbol in ["UST", "AMPL"]:
        return
    token = aave_token.address
    atoken = interface.AaveV2Token(aave_token.aTokenAddress)
    amount = 10**aave_token.decimals

    mint_tokens_for(token, invoker, amount)

    calldata_supply = clend_aave.supply.encode_input(aave_token.pool, token, amount, alice)

    invoker.invoke([clend_aave], [calldata_supply], {"from": alice})
    assert_approx(atoken.balanceOf(alice), amount)


def test_withdraw(clend_aave, invoker, aave_token: AaveAssetInfo, alice, interface):
    if aave_token.symbol in ["UST", "AMPL"]:
        return
    token = interface.ERC20Detailed(aave_token.address)
    atoken = aave_token.aTokenAddress
    amount = 10**aave_token.decimals

    mint_tokens_for(atoken, invoker, amount + 1)

    calldata_withdraw = clend_aave.withdraw.encode_input(aave_token.pool, atoken, amount - 1, alice)
    invoker.invoke([clend_aave], [calldata_withdraw], {"from": alice})

    assert_approx(token.balanceOf(alice), amount)


@pytest.mark.parametrize("mode", InterestRateMode.list(), ids=InterestRateMode.keys())
def test_borrow_and_repay(
    clend_aave, cmove, invoker, aave_token: AaveAssetInfo, alice, mode, interface
):
    if aave_token.symbol in ["AAVE", "xSUSHI", "UST", "AMPL"]:
        return

    token = interface.ERC20Detailed(aave_token.address)
    vdebt = interface.AaveV2DebtToken(aave_token.variableDebtTokenAddress)
    sdebt = interface.AaveV2DebtToken(aave_token.stableDebtTokenAddress)
    amount = 10**aave_token.decimals

    # use USDC for collateral, except to borrow usdc - then use wbtc
    collateral_token = (
        get_chain_token("wbtc") if aave_token.symbol == "USDC" else get_chain_token("usdc")
    )
    collateral = collateral_token["address"]
    collateral_amount = 100_000 * 10 ** collateral_token["decimals"]
    # This will give error #11 when the price of WBTC is greater than 100,000 USD
    mint_tokens_for(collateral, invoker, collateral_amount)

    calldata_supply = clend_aave.supply.encode_input(
        aave_token.pool, collateral, collateral_amount, alice
    )

    invoker.invoke([clend_aave], [calldata_supply], {"from": alice})

    if mode == InterestRateMode.STABLE:
        sdebt.approveDelegation(invoker, 2**256 - 1, {"from": alice})
    elif mode == InterestRateMode.VARIABLE:
        vdebt.approveDelegation(invoker, 2**256 - 1, {"from": alice})

    calldata_borrow = clend_aave.borrow.encode_input(aave_token.pool, token, amount / 10, mode)
    calldata_move_out = cmove.moveAllERC20Out.encode_input(token, alice)
    try:
        invoker.invoke([clend_aave, cmove], [calldata_borrow, calldata_move_out], {"from": alice})
    except VirtualMachineError as e:
        if e.revert_msg in ["7", "12"]:
            # 7: "Borrowing is not enabled"
            # 12: "Stable borrowing not enabled"
            return
        else:
            raise e from None

    assert_approx(token.balanceOf(alice), amount / 10)

    calldata_repay = clend_aave.repay.encode_input(aave_token.pool, token, amount / 10, mode)
    token.transfer(invoker, amount / 10, {"from": alice})
    invoker.invoke([clend_aave], [calldata_repay], {"from": alice})
    assert_approx(token.balanceOf(alice), 0)
