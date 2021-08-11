import time

import pytest
from helpers import get_dai_for_user


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


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


# This test won't work now, as we won't allow users to interact directly with uniswap
"""
@pytest.mark.require_network("hardhat-fork")
def test_buy_dai_via_delegate_invoker(user, dai, weth, uni_router, invoker):
    path = [weth.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(2700 * 1e18, path, user, deadline)
    invoker.invokeDelegate(uni_router.address, calldata, {"from": user, "value": 1e18})
    assert dai.balanceOf(user) > 2700 * 1e18
"""


@pytest.mark.require_network("hardhat-fork")
def test_swap_dai_usdc_via_delegate_invoker_individually(
    deployer, dai, usdc, cswap, cmove, weth, uni_router, invoker
):
    get_dai_for_user(dai, deployer, weth, uni_router)

    # Approve invoker to spend 1000 Dai
    dai.approve(invoker.address, 1000 * 1e18, {"from": deployer})
    assert dai.allowance(deployer, invoker.address) == 1000 * 1e18

    # Move 1000 Dai to invoker
    calldata_move = cmove.move.encode_input(dai.address, invoker.address, 1000 * 1e18)
    invoker.invokeDelegate(cmove.address, calldata_move, {"from": deployer})
    assert dai.balanceOf(invoker.address) == 1000 * 1e18

    # Swap 1000 Dai for some USDC
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )
    invoker.invokeDelegate(cswap.address, calldata_swap, {"from": deployer})
    assert usdc.balanceOf(deployer) > 995 * 1e6


@pytest.mark.require_network("hardhat-fork")
def test_swap_dai_usdc_via_delegate_invoker_combo(
    deployer, dai, usdc, cswap, cmove, weth, uni_router, invoker
):
    get_dai_for_user(dai, deployer, weth, uni_router)

    # Approve invoker to spend 1000 Dai
    dai.approve(invoker.address, 1000 * 1e18, {"from": deployer})
    assert dai.allowance(deployer, invoker.address) == 1000 * 1e18

    # Move 1000 Dai to invoker and swap for USDC
    calldata_move = cmove.move.encode_input(dai.address, invoker.address, 1000 * 1e18)
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )

    # Move 1000 Dai to invoker and swap for USDC
    calldata_move = cmove.move.encode_input(dai.address, invoker.address, 1000 * 1e18)
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )

    invoker.invoke(
        [cmove.address, cswap.address], [calldata_move, calldata_swap], {"from": deployer}
    )
    assert usdc.balanceOf(deployer) > 995 * 1e6
