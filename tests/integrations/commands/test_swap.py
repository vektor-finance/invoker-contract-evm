import time

from brownie.test import given, strategy


def test_buy_token(alice, weth, uni_router, token):
    if token == weth:
        return
    amount_in = 1e18
    path = [weth.address, token.address]
    [_, amount_out] = uni_router.getAmountsOut(amount_in, path)
    uni_router.swapExactETHForTokens(
        amount_out, path, alice, time.time() + 1, {"from": alice, "value": amount_in}
    )
    assert token.balanceOf(alice) >= amount_out


@given(amount_in=strategy("uint256", min_value="1", max_value="1000 ether"))
def test_buy_with_invoker(alice, weth, uni_router, token, invoker, venue_cswap, amount_in):
    """Test simple BUY via invoker"""
    if token == weth:
        return
    path = [weth.address, token.address]
    [_, amount_out] = uni_router.getAmountsOut(amount_in, path)

    if amount_out == 0:
        return

    calldata_wrap = venue_cswap.wrapEth.encode_input(amount_in)
    calldata_buy = venue_cswap.swapUniswapIn.encode_input(amount_in, amount_out, path)

    invoker.invoke(
        [venue_cswap.address, venue_cswap.address],
        [calldata_wrap, calldata_buy],
        {"from": alice, "value": amount_in},
    )
    assert token.balanceOf(invoker.address) >= amount_out


@given(value=strategy("uint256", max_value="1000 ether"))
def test_wrap_native(alice, invoker, weth, cswap, value):
    starting_balance = alice.balance()
    calldata_wrap = cswap.wrapEth.encode_input(value)
    invoker.invoke([cswap.address], [calldata_wrap], {"from": alice, "value": value})
    assert alice.balance() == starting_balance - value
    assert weth.balanceOf(invoker) == value


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_native(alice, invoker, weth, cswap, value):
    calldata_unwrap = cswap.unwrapWeth.encode_input(value)
    # charitable donation from maker contract:
    weth.transfer(invoker, value, {"from": "0x2F0b23f53734252Bda2277357e97e1517d6B042A"})
    invoker.invoke([cswap.address], [calldata_unwrap], {"from": alice})
    assert invoker.balance() == value
    assert weth.balanceOf(invoker) == 0


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_all_native(alice, invoker, weth, venue_cswap, value):
    calldata_unwrap_all = venue_cswap.unwrapAllWeth.encode_input()
    # charitable donation from maker contract:
    weth.transfer(invoker, value, {"from": "0x2F0b23f53734252Bda2277357e97e1517d6B042A"})
    invoker.invoke([venue_cswap.address], [calldata_unwrap_all], {"from": alice})
    assert invoker.balance() == value
    assert weth.balanceOf(invoker) == 0
