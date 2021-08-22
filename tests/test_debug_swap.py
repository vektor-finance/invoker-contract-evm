import pytest
from helpers import get_dai_for_user


@pytest.mark.require_network("hardhat-fork")
def test_buy_link(alice, weth, link, dai, uni_router, invoker, cswap):
    get_dai_for_user(dai, alice, weth, uni_router)
    dai.approve(invoker.address, 100 * 1e18, {"from": alice})
    calldata_swap = cswap.DEBUG_swapIn.encode_input(100 * 1e18, [dai.address, link.address])
    invoker.invoke([cswap.address], [calldata_swap], {"from": alice})
    assert link.balanceOf(alice) > 0
