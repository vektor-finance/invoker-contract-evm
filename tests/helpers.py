import time


def get_dai_for_user(dai, user, weth, uni_router):
    path = [weth.address, dai.address]
    uni_router.swapExactETHForTokens(
        0, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert dai.balanceOf(user) > 0
