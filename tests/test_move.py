import time

import brownie
import pytest
from helpers import get_dai_for_user


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_move_dai(dai, alice, bob, weth, uni_router, invoker, cmove):
    get_dai_for_user(dai, alice, weth, uni_router)
    calldata_dai_alice_to_bob = cmove.move.encode_input(dai.address, bob.address, 1000 * 1e18)
    dai.approve(invoker.address, 1000 * 1e18, {"from": alice})
    invoker.invoke([cmove.address], [calldata_dai_alice_to_bob], {"from": alice})
    assert dai.balanceOf(bob.address) == 1000 * 1e18


def test_move_dai_should_revert_if_insufficient_balance(
    dai, alice, bob, weth, uni_router, invoker, cmove
):
    get_dai_for_user(dai, alice, weth, uni_router)
    calldata_dai_alice_to_bob = cmove.move.encode_input(dai.address, bob.address, 10000 * 1e18)
    dai.approve(invoker.address, 10000 * 1e18, {"from": alice})
    with brownie.reverts("Dai/insufficient-balance"):
        invoker.invoke([cmove.address], [calldata_dai_alice_to_bob], {"from": alice})


def test_move_dai_should_revert_if_insufficient_allowance(
    dai, alice, bob, weth, uni_router, invoker, cmove
):
    get_dai_for_user(dai, alice, weth, uni_router)
    calldata_dai_alice_to_bob = cmove.move.encode_input(dai.address, bob.address, 1000 * 1e18)
    with brownie.reverts("Dai/insufficient-allowance"):
        invoker.invoke([cmove.address], [calldata_dai_alice_to_bob], {"from": alice})


def get_world_token_for_user(user, weth, world, uni_router):
    path = [weth.address, world.address]
    uni_router.swapExactETHForTokens(
        0, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert world.balanceOf(user) > 0


def test_move_world_token(world, alice, bob, weth, uni_router, invoker, cmove):
    get_world_token_for_user(alice, weth, world, uni_router)
    world.approve(invoker.address, 100 * 1e18, {"from": alice})
    calldata_world_alice_to_bob = cmove.move.encode_input(world.address, bob.address, 100 * 1e18)
    with brownie.reverts("CMove: Invalid balance after move"):
        invoker.invoke([cmove.address], [calldata_world_alice_to_bob], {"from": alice})
