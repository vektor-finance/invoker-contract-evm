import time


def get_dai_for_user(dai, user, weth, uni_router):
    path = [weth.address, dai.address]
    uni_router.swapExactETHForTokens(
        0, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert dai.balanceOf(user) > 0


# Roles
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"
# keccak256("APPROVED_COMMAND_IMPLEMENTATION")
