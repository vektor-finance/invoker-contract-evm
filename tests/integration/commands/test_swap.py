import time

import pytest
from brownie.test import given, strategy
from hypothesis import assume


def fn_native_for_token(uni_router, chain_id):
    if chain_id == 43114:
        return uni_router.swapExactAVAXForTokens
    return uni_router.swapExactETHForTokens


def fn_token_for_native(uni_router, chain_id):
    if chain_id == 43114:
        return uni_router.swapExactTokensForAVAX
    return uni_router.swapExactTokensForETH


def test_buy_token(alice, wnative, uni_router, token, connected_chain):
    if token == wnative:
        pytest.skip("Cannot buy WNATIVE")
    amount_in = 1e18
    path = [wnative.address, token.address]
    [_, amount_out] = uni_router.getAmountsOut(amount_in, path)

    # When amount_out is zero there is insufficient liquidity.
    # This is a 'bad' example and should be ignored (not failed)
    assume(amount_out > 0)

    fn = fn_native_for_token(uni_router, connected_chain["chain_id"])

    fn(amount_out, path, alice, time.time() + 1, {"from": alice, "value": amount_in})
    assert token.balanceOf(alice) >= amount_out


@given(value=strategy("uint256", min_value="1", max_value="100"))
def test_buy_with_invoker(alice, wnative, uni_router, token, invoker, cswap, value):
    """Test simple BUY via invoker"""
    if token == wnative:
        pytest.skip("Cannot buy WNATIVE")
    amount_in = value * 1e18  # wnative decimals
    path = [wnative.address, token.address]
    [_, amount_out] = uni_router.getAmountsOut(amount_in, path)

    assume(amount_out > 0)

    calldata_wrap = cswap.wrapNative.encode_input(amount_in)
    calldata_buy = cswap.swapUniswapIn.encode_input(amount_in, amount_out, path)

    invoker.invoke(
        [cswap.address, cswap.address],
        [calldata_wrap, calldata_buy],
        {"from": alice, "value": amount_in},
    )
    assert token.balanceOf(invoker.address) >= amount_out


def test_sell_token(alice, wnative, uni_router, tokens_for_alice, connected_chain):
    if tokens_for_alice == wnative:
        pytest.skip("Cannot sell wnative")
    amount_in = 100 * (10 ** tokens_for_alice.decimals())
    path = [tokens_for_alice.address, wnative.address]
    prev_balance = alice.balance()
    [_, amount_out] = uni_router.getAmountsOut(amount_in, path)
    tokens_for_alice.approve(uni_router.address, amount_in, {"from": alice})

    assume(amount_out > 0)

    fn = fn_token_for_native(uni_router, connected_chain["chain_id"])

    fn(amount_in, amount_out, path, alice, time.time() + 1, {"from": alice})
    assert alice.balance() >= prev_balance + amount_out


@given(amount_in=strategy("uint256", min_value="1", max_value="100"))
def test_sell_with_invoker(
    alice, wnative, uni_router, tokens_for_alice, invoker, cmove, cswap, amount_in
):
    value = amount_in * (10 ** tokens_for_alice.decimals())
    """Test simple SELL via invoker"""
    if tokens_for_alice == wnative:
        pytest.skip("Cannot sell wnative")
    path = [tokens_for_alice.address, wnative.address]
    [_, amount_out] = uni_router.getAmountsOut(value, path)

    assume(amount_out > 0)

    calldata_move = cmove.moveERC20In.encode_input(tokens_for_alice, value)
    calldata_sell = cswap.swapUniswapIn.encode_input(value, amount_out, path)

    tokens_for_alice.approve(invoker.address, value, {"from": alice})

    invoker.invoke(
        [cmove.address, cswap.address],
        [calldata_move, calldata_sell],
        {"from": alice},
    )
    assert wnative.balanceOf(invoker.address) >= amount_out


@given(value=strategy("uint256", max_value="1000 ether"))
def test_wrap_native(alice, invoker, wnative, cswap, value):
    starting_balance = alice.balance()
    calldata_wrap = cswap.wrapNative.encode_input(value)
    invoker.invoke([cswap.address], [calldata_wrap], {"from": alice, "value": value})
    assert alice.balance() == starting_balance - value
    assert wnative.balanceOf(invoker) == value


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_native(alice, invoker, wnative, cswap, value, bob):
    # bob mints wrapped native and sends to invoker
    wnative.deposit({"from": bob, "value": value})
    wnative.transfer(invoker, value, {"from": bob})
    calldata_unwrap = cswap.unwrapWrappedNative.encode_input(value)
    invoker.invoke([cswap.address], [calldata_unwrap], {"from": alice})
    assert invoker.balance() == value
    assert wnative.balanceOf(invoker) == 0


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_all_native(alice, invoker, wnative, cswap, value, bob):
    # bob mints wrapped native and sends to invoker
    wnative.deposit({"from": bob, "value": value})
    wnative.transfer(invoker, value, {"from": bob})

    calldata_unwrap_all = cswap.unwrapAllWrappedNative.encode_input()
    invoker.invoke([cswap.address], [calldata_unwrap_all], {"from": alice})
    assert invoker.balance() == value
    assert wnative.balanceOf(invoker) == 0
