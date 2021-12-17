import time


def get_dai_for_user(dai, user, weth, uni_router):
    path = [weth.address, dai.address]
    uni_router.swapExactETHForTokens(
        0, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert dai.balanceOf(user) > 0


def get_world_token_for_user(user, weth, world, uni_router):
    path = [weth.address, world.address]
    uni_router.swapExactETHForTokens(
        0, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert world.balanceOf(user) > 0


def get_weth(weth, invoker, value):
    # maker contract has 1.8M WETH so we can "borrow" some for testing purposes
    maker_contract = "0x2F0b23f53734252Bda2277357e97e1517d6B042A"
    weth.transfer(invoker, value, {"from": maker_contract})
    assert weth.balanceOf(invoker) == value


# Roles
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"
# keccak256("APPROVED_COMMAND_IMPLEMENTATION")
