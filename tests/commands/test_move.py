import brownie
from brownie.test import given, strategy
from helpers import get_dai_for_user, get_world_token_for_user


def test_move_dai_in(dai, alice, weth, uni_router, invoker, cmove):
    get_dai_for_user(dai, alice, weth, uni_router)
    dai.approve(invoker.address, 1000 * 1e18, {"from": alice})
    calldata_move_dai_in = cmove.moveERC20In.encode_input(dai.address, 1000 * 1e18)
    invoker.invoke([cmove.address], [calldata_move_dai_in], {"from": alice})
    assert dai.balanceOf(invoker.address) == 1000 * 1e18


def test_move_dai_out(dai, alice, bob, weth, uni_router, invoker, cmove):
    get_dai_for_user(dai, alice, weth, uni_router)
    dai.transfer(invoker.address, 1000 * 1e18, {"from": alice})
    calldata_move_dai_out = cmove.moveERC20Out.encode_input(dai.address, bob.address, 1000 * 1e18)
    invoker.invoke([cmove.address], [calldata_move_dai_out], {"from": alice})
    assert dai.balanceOf(bob.address) == 1000 * 1e18


def test_move_dai_all_out(dai, alice, bob, weth, uni_router, invoker, cmove):
    get_dai_for_user(dai, alice, weth, uni_router)
    alice_starting_balance = dai.balanceOf(alice.address)
    bob_starting_balance = dai.balanceOf(bob.address)
    amount_dai = 1000 * 1e18
    dai.approve(invoker.address, amount_dai, {"from": alice})
    calldata_move_dai_in = cmove.moveERC20In.encode_input(dai.address, amount_dai)
    calldata_move_dai_out_all = cmove.moveERC20OutAll.encode_input(dai.address, bob.address)
    invoker.invoke(
        [cmove.address, cmove.address],
        [calldata_move_dai_in, calldata_move_dai_out_all],
        {"from": alice},
    )
    assert dai.balanceOf(invoker.address) == 0
    assert dai.balanceOf(alice.address) == alice_starting_balance - amount_dai
    assert dai.balanceOf(bob.address) == bob_starting_balance + amount_dai


def test_move_dai_in_should_revert_if_insufficient_balance(dai, alice, invoker, cmove):
    dai.approve(invoker.address, 1000 * 1e18, {"from": alice})
    calldata_move_dai_in = cmove.moveERC20In.encode_input(dai.address, 1000 * 1e18)
    with brownie.reverts("Dai/insufficient-balance"):
        invoker.invoke([cmove.address], [calldata_move_dai_in], {"from": alice})


def test_move_dai_out_should_revert_if_insufficient_balance(dai, alice, bob, invoker, cmove):
    calldata_move_dai_out = cmove.moveERC20Out.encode_input(dai.address, bob.address, 1000 * 1e18)
    with brownie.reverts("Dai/insufficient-balance"):
        invoker.invoke([cmove.address], [calldata_move_dai_out], {"from": alice})


def test_move_dai_in_should_revert_if_insufficient_allowance(
    dai, alice, weth, uni_router, invoker, cmove
):
    get_dai_for_user(dai, alice, weth, uni_router)
    calldata_move_dai_in = cmove.moveERC20In.encode_input(dai.address, 1000 * 1e18)
    with brownie.reverts("Dai/insufficient-allowance"):
        invoker.invoke([cmove.address], [calldata_move_dai_in], {"from": alice})


# world token is a deflationary token (takes 3% fees on transfer)
def test_move_world_token_in(world, alice, bob, weth, uni_router, invoker, cmove):
    get_world_token_for_user(alice, weth, world, uni_router)
    world.approve(invoker.address, 100 * 1e18, {"from": alice})
    calldata_world_alice_to_invoker = cmove.moveERC20In.encode_input(world.address, 100 * 1e18)
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_world_alice_to_invoker], {"from": alice})


def test_move_world_token_out(world, alice, bob, weth, uni_router, invoker, cmove):
    get_world_token_for_user(alice, weth, world, uni_router)
    world.transfer(invoker.address, 110 * 1e18, {"from": alice})
    calldata_world_invoker_to_bob = cmove.moveERC20Out.encode_input(
        world.address, bob.address, 100 * 1e18
    )
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_world_invoker_to_bob], {"from": alice})


def test_move_world_token_out_all(world, alice, bob, weth, uni_router, invoker, cmove):
    get_world_token_for_user(alice, weth, world, uni_router)
    world.transfer(invoker.address, 110 * 1e18, {"from": alice})
    calldata_world_invoker_to_bob = cmove.moveERC20OutAll.encode_input(world.address, bob.address)
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_world_invoker_to_bob], {"from": alice})


@given(value=strategy("uint256", max_value="1000 ether"), to=strategy("address"))
def test_move_eth_to_single_address(alice, to, invoker, cmove, value):
    alice_starting_balance = alice.balance()
    to_starting_balance = to.balance()
    calldata_transfer_one_eth = cmove.moveEth.encode_input(to.address, value)
    invoker.invoke([cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": value})
    if alice is not to:
        assert alice.balance() == alice_starting_balance - value
        assert to.balance() == to_starting_balance + value


@given(
    value1=strategy("uint256", max_value="500 ether"),
    user1=strategy("address"),
    value2=strategy("uint256", max_value="500 ether"),
    user2=strategy("address"),
)
def test_move_eth_to_multiple_addresses(alice, user1, user2, value1, value2, invoker, cmove):
    alice_starting_balance = alice.balance()
    user1_starting_balance = user1.balance()
    user2_starting_balance = user2.balance()
    calldata_transfer_eth_to_user1 = cmove.moveEth.encode_input(user1.address, value1)
    calldata_transfer_eth_to_user2 = cmove.moveEth.encode_input(user2.address, value2)
    invoker.invoke(
        [cmove.address, cmove.address],
        [calldata_transfer_eth_to_user1, calldata_transfer_eth_to_user2],
        {"from": alice, "value": value1 + value2},
    )
    if alice in [user1, user2]:
        pass
    else:
        assert alice.balance() == alice_starting_balance - value1 - value2
        if user1 is not user2:
            assert user1.balance() == user1_starting_balance + value1
            assert user2.balance() == user2_starting_balance + value2
