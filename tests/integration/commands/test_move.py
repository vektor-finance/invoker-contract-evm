import brownie
import hypothesis
from brownie import Contract, interface
from brownie.test import given, strategy

from data.strategies import token_strategy
from data.test_helpers import mint_tokens_for


def generate_move_data(data):
    a = data.draw(token_strategy(), label="Token")
    user = data.draw(strategy("address"), label="User")
    token = Contract.from_abi(a["name"], a["address"], interface.ERC20Detailed.abi)
    max_amount = mint_tokens_for(token, user)
    amount = data.draw(strategy("uint256", max_value=max_amount, min_value=1), label="Input Amount")
    return (token, user, amount)


@given(data=hypothesis.strategies.data())
def test_move_erc20_in(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    start_balance = token.balanceOf(alice)
    token.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(token.address, amount)
    invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})
    assert token.balanceOf(invoker.address) == amount
    assert token.balanceOf(alice) == start_balance - amount


@given(data=hypothesis.strategies.data())
def test_move_erc20_out(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    start_balance = token.balanceOf(alice)
    token.transfer(invoker.address, start_balance, {"from": alice})
    calldata_move_out = cmove.moveERC20Out.encode_input(token.address, alice, amount)
    invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})
    assert token.balanceOf(invoker.address) == start_balance - amount
    assert token.balanceOf(alice) == amount


@given(data=hypothesis.strategies.data())
def test_move_all_erc20_out(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    start_balance = token.balanceOf(alice)
    token.transfer(invoker.address, amount, {"from": alice})
    calldata_move_all_out = cmove.moveAllERC20Out.encode_input(token.address, alice)
    invoker.invoke([cmove.address], [calldata_move_all_out], {"from": alice})
    assert token.balanceOf(invoker.address) == 0
    assert token.balanceOf(alice) == start_balance


@given(data=hypothesis.strategies.data())
def test_fail_insufficient_balance_move_erc20_in(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    large_amount = data.draw(strategy("uint256", min_value=amount + 1))
    token.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(token.address, large_amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


@given(data=hypothesis.strategies.data())
def test_fail_insufficient_allowance_move_erc20_in(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    insufficient_amount = data.draw(strategy("uint256", max_value=amount - 1))
    token.approve(invoker.address, insufficient_amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(token.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


@given(data=hypothesis.strategies.data())
def test_fail_insufficient_balance_move_erc20_out(data, invoker, cmove):
    (token, alice, amount) = generate_move_data(data)
    insufficient_amount = data.draw(strategy("uint256", max_value=amount - 1))
    token.transfer(invoker.address, insufficient_amount, {"from": alice})
    calldata_move_out = cmove.moveERC20Out.encode_input(token.address, alice, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})
