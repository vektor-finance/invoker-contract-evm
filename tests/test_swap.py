import math
import time

import pytest
from brownie.test import given, strategy
from helpers import get_dai_for_user


@pytest.mark.require_network("hardhat-fork")
def test_buy_dai(deployer, dai, weth, uni_router):
    path = [weth.address, dai.address]
    uni_router.swapExactETHForTokens(
        2700 * 1e18, path, deployer, time.time() + 1, {"from": deployer, "value": 1e18}
    )
    assert dai.balanceOf(deployer) > 2700 * 1e18


@pytest.mark.require_network("hardhat-fork")
def test_buy_dai_via_invoker(deployer, dai, weth, uni_router, invoker):
    path = [weth.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(
        2700 * 1e18, path, deployer, time.time() + 1
    )
    invoker.invokeStatic(uni_router.address, calldata, 1e18, {"from": deployer, "value": 1e18})
    assert dai.balanceOf(deployer) > 2700 * 1e18


@pytest.mark.require_network("hardhat-fork")
@given(value=strategy("uint256", max_value="1000 ether", min_value=2e12))
def test_swap_dai_usdc_via_delegate_invoker_individually(
    alice, dai, usdc, cswap, cmove, weth, uni_router, invoker, value
):
    get_dai_for_user(dai, alice, weth, uni_router)
    # Approve invoker to spend Dai
    dai.approve(invoker.address, value, {"from": alice})
    assert dai.allowance(alice.address, invoker.address) == value
    # Move Dai to invoker
    calldata_move = cmove.moveERC20In.encode_input(dai.address, value)
    invoker.invoke([cmove.address], [calldata_move], {"from": alice})
    assert dai.balanceOf(invoker.address) == value
    # Swap Dai for USDC
    min_value = math.floor(0.9 * value / 1e12)  # dai is 1e18, usdc is 1e6 decimals
    calldata_swap = cswap.swapUniswapIn.encode_input(value, min_value, [dai.address, usdc.address])
    invoker.invoke([cswap.address], [calldata_swap], {"from": alice})
    assert usdc.balanceOf(invoker.address) >= min_value


@pytest.mark.require_network("hardhat-fork")
@given(value=strategy("uint256", max_value="1000 ether", min_value=2e12))
def test_swap_dai_usdc_via_delegate_invoker_combo(
    alice, dai, usdc, cswap, cmove, weth, uni_router, invoker, value
):
    get_dai_for_user(dai, alice, weth, uni_router)
    # Approve invoker to spend Dai
    dai.approve(invoker.address, value, {"from": alice})
    assert dai.allowance(alice.address, invoker.address) == value
    # Move Dai to invoker
    calldata_move = cmove.moveERC20In.encode_input(dai.address, value)
    # Swap Dai for USDC
    min_value = math.floor(0.9 * value / 1e12)  # dai is 1e18, usdc is 1e6 decimals
    calldata_swap = cswap.swapUniswapIn.encode_input(value, min_value, [dai.address, usdc.address])
    invoker.invoke([cmove.address, cswap.address], [calldata_move, calldata_swap], {"from": alice})
    assert usdc.balanceOf(invoker.address) >= min_value


@pytest.mark.require_network("hardhat-fork")
@given(value=strategy("uint256", max_value=900 * 1e6, min_value=1))
def test_swap_dai_usdc_out(alice, dai, usdc, cswap, cmove, weth, uni_router, invoker, value):
    get_dai_for_user(dai, alice, weth, uni_router)
    # Approve invoker to spend Dai
    max_value = 1.1 * value * 1e12
    dai.approve(invoker.address, max_value, {"from": alice})
    assert dai.allowance(alice.address, invoker.address) == max_value
    # Move Dai to invoker
    calldata_move = cmove.moveERC20In.encode_input(dai.address, max_value)
    # Swap Dai for USDC
    calldata_swap = cswap.swapUniswapOut.encode_input(value, max_value, [dai.address, usdc.address])
    invoker.invoke([cmove.address, cswap.address], [calldata_move, calldata_swap], {"from": alice})
    assert usdc.balanceOf(invoker.address) == value


@pytest.mark.require_network("hardhat-fork")
@given(value=strategy("uint256", max_value="1000 ether"))
def test_wrap_eth(alice, invoker, cswap, weth, value):
    starting_balance = alice.balance()
    starting_weth_balance = weth.balanceOf(invoker)
    calldata_wrap_eth = cswap.wrapEth.encode_input(value)
    invoker.invoke([cswap.address], [calldata_wrap_eth], {"from": alice, "value": value})
    assert alice.balance() == starting_balance - value
    assert weth.balanceOf(invoker) == starting_weth_balance + value


@given(value=strategy("uint256", max_value="1000 ether"))
@pytest.mark.require_network("hardhat-fork")
def test_unwrapwrap_eth(alice, invoker, cswap, weth, value):
    # maker contract has 1.8M WETH so we can "borrow" some for testing purposes
    maker_contract = "0x2F0b23f53734252Bda2277357e97e1517d6B042A"
    weth.transfer(invoker, value, {"from": maker_contract})
    assert weth.balanceOf(invoker) == value

    starting_weth_balance = weth.balanceOf(invoker)
    starting_balance = invoker.balance()
    calldata_unwrap_eth = cswap.unwrapEth.encode_input(value)
    invoker.invoke([cswap.address], [calldata_unwrap_eth], {"from": alice})
    assert invoker.balance() == starting_balance + value
    assert weth.balanceOf(invoker) == starting_weth_balance - value
