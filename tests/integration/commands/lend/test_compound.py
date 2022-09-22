import pytest

from data.chain import get_chain_token
from data.test_helpers import mint_tokens_for


@pytest.mark.parametrize("collat_token", ["WBTC", "COMP", "WETH", "LINK", "UNI"])
def test_supply_and_withdraw(clend_compound, collat_token, invoker, alice, interface):
    token = interface.ERC20Detailed(get_chain_token(collat_token)["address"])
    mint_amount = 1e8
    supply_amount = 1e6
    withdraw_amount = 1e5
    mint_tokens_for(token, alice, mint_amount)

    comet = interface.CompoundV3Comet("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

    comet.allow(invoker, True, {"from": alice})
    token.approve(comet, mint_amount, {"from": alice})

    calldata_supply = clend_compound.supply.encode_input(comet, token, supply_amount, alice)
    invoker.invoke([clend_compound], [calldata_supply], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount
    assert comet.userCollateral(alice, token)[0] == supply_amount

    calldata_withdraw = clend_compound.withdraw.encode_input(comet, token, withdraw_amount, alice)
    invoker.invoke([clend_compound], [calldata_withdraw], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount + withdraw_amount
    assert comet.userCollateral(alice, token)[0] == supply_amount - withdraw_amount


def assert_approx(a, b):
    # equivalent to assert b == a +- 2
    assert a - 2 <= b <= a + 2


def test_deposit_and_withdraw(clend_compound, invoker, alice, interface):
    token = interface.ERC20Detailed(get_chain_token("USDC")["address"])
    mint_amount = 1e8
    supply_amount = 1e6
    withdraw_amount = 1e5
    mint_tokens_for(token, alice, mint_amount)

    comet = interface.CompoundV3Comet("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

    comet.allow(invoker, True, {"from": alice})
    token.approve(comet, mint_amount, {"from": alice})

    calldata_supply = clend_compound.repay.encode_input(comet, supply_amount, alice)
    invoker.invoke([clend_compound], [calldata_supply], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount
    assert_approx(comet.balanceOf(alice), supply_amount)

    calldata_withdraw = clend_compound.borrow.encode_input(comet, withdraw_amount, alice)
    invoker.invoke([clend_compound], [calldata_withdraw], {"from": alice})

    assert token.balanceOf(alice) == mint_amount - supply_amount + withdraw_amount
    assert_approx(comet.balanceOf(alice), supply_amount - withdraw_amount)
