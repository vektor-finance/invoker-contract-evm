import pytest
from brownie import CMove, CSwap, Invoker, accounts
from helpers import get_dai_for_user

deadline = 1659715115
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


@pytest.fixture(scope="module")
def invoker(cmove, cswap):
    contract = accounts[0].deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cmove.address, {"from": accounts[0]})  # approve commands
    contract.grantRole(APPROVED_COMMAND, cswap.address, {"from": accounts[0]})
    return contract


@pytest.fixture(scope="module")
def cswap():
    return accounts[0].deploy(CSwap)


@pytest.fixture(scope="module")
def cmove():
    return accounts[0].deploy(CMove)


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.mark.require_network("hardhat-fork")
def test_buy_dai(user, dai, weth, uni_router):
    path = [weth.address, dai.address]
    uni_router.swapExactETHForTokens(
        2700 * 1e18, path, user, deadline, {"from": user, "value": 1e18}
    )
    assert dai.balanceOf(user) > 2700 * 1e18


@pytest.mark.require_network("hardhat-fork")
def test_buy_dai_via_invoker(user, dai, weth, uni_router, invoker):
    path = [weth.address, dai.address]
    calldata = uni_router.swapExactETHForTokens.encode_input(2700 * 1e18, path, user, deadline)
    invoker.invokeStatic(uni_router.address, calldata, 1e18, {"from": user, "value": 1e18})
    assert dai.balanceOf(user) > 2700 * 1e18


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
    user, dai, usdc, cswap, cmove, weth, uni_router, invoker
):
    get_dai_for_user(dai, user, weth, uni_router)

    # Approve invoker to spend 1000 Dai
    dai.approve(invoker.address, 1000 * 1e18, {"from": user})
    assert dai.allowance(user, invoker.address) == 1000 * 1e18

    # Move 1000 Dai to invoker
    calldata_move = cmove.move.encode_input(dai.address, user, invoker.address, 1000 * 1e18)
    invoker.invokeDelegate(cmove.address, calldata_move, {"from": user})
    assert dai.balanceOf(invoker.address) == 1000 * 1e18

    # Swap 1000 Dai for some USDC
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )
    invoker.invokeDelegate(cswap.address, calldata_swap, {"from": user})
    assert usdc.balanceOf(user) > 995 * 1e6


@pytest.mark.require_network("hardhat-fork")
def test_swap_dai_usdc_via_delegate_invoker_combo(
    user, dai, usdc, cswap, cmove, weth, uni_router, invoker
):
    get_dai_for_user(dai, user, weth, uni_router)

    # Approve invoker to spend 1000 Dai
    dai.approve(invoker.address, 1000 * 1e18, {"from": user})
    assert dai.allowance(user, invoker.address) == 1000 * 1e18

    # Move 1000 Dai to invoker and swap for USDC
    calldata_move = cmove.move.encode_input(dai.address, user, invoker.address, 1000 * 1e18)
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )

    # Move 1000 Dai to invoker and swap for USDC
    calldata_move = cmove.move.encode_input(dai.address, user, invoker.address, 1000 * 1e18)
    calldata_swap = cswap.swapExactTokensForTokens.encode_input(
        1000 * 1e18, 0, [dai.address, usdc.address]
    )

    invoker.invoke([cmove.address, cswap.address], [calldata_move, calldata_swap], {"from": user})
    assert usdc.balanceOf(user) > 995 * 1e6
