# Move and Swap
import pytest
from brownie import ZERO_ADDRESS, Contract, interface, reverts


@pytest.fixture(scope="module")
def dai():
    yield Contract.from_abi(
        "Dai", "0x6b175474e89094c44da98b954eedeac495271d0f", interface.IERC20.abi
    )


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_abi(
        "WETH", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", interface.IWETH.abi
    )


def test_swap_eth_for_dai(invoker, alice, cmove, cswap, cwrap, weth, dai, uni_router):
    """
    ALICE wants to swap her ETH for DAI
    Invoke:
    1. Wrap ETH -> WETH
    2. Swap WETH -> DAI
    3. Move DAI -> Alice
    """

    value = "1 ether"
    starting_balance = alice.balance()

    # 1. Wrap ETH
    calldata_wrap_eth = cwrap.wrapNative.encode_input(value)

    # 2. Swap WETH -> Dai
    calldata_swap_weth_dai = cswap.sell.encode_input(
        value, weth, dai, 0, (uni_router, [weth, dai], ZERO_ADDRESS, 0)
    )

    # 3. Move Dai -> Alice
    calldata_move_dai = cmove.moveERC20Out.encode_input(dai.address, alice.address, 100 * 1e18)

    invoker.invoke(
        [cwrap.address, cswap.address, cmove.address],
        [calldata_wrap_eth, calldata_swap_weth_dai, calldata_move_dai],
        {"from": alice, "value": value},
    )

    assert alice.balance() == starting_balance - "1 ether"
    assert dai.balanceOf(alice) == 100 * 1e18


def test_swap_dai_to_eth_and_disperse(
    invoker, bob, cmove, cwrap, uni_router, cswap, weth, dai, accounts
):
    """
    Bob wants to quickly fund three accounts to farm airdrops
    First: Approve Dai on invoker
    Invoke:
    1. Move Dai -> Invoker
    2. Swap Dai -> WETH
    3. Unwrap WETH -> ETH
    4. Move ETH -> Account 3
    5. Move ETH -> Account 4
    6. Move ETH -> Account 5
    Note accounts 0,1,2 already reserved
    """

    # First get the user one eth worth of dai
    dai.transfer(bob.address, 2000 * 1e18, {"from": "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7"})
    dai.approve(invoker.address, 2000 * 1e18, {"from": bob.address})

    # 1. Move Dai to invoker
    calldata_move_dai = cmove.moveERC20In.encode_input(dai.address, 2000 * 1e18)

    # 2. Swap Dai -> WETH
    # will stop working when eth > 6000 dai
    calldata_swap_dai_eth = cswap.buy.encode_input(
        "0.3 ether",
        weth,
        dai,
        2000 * 1e18,
        (uni_router, [dai, weth], ZERO_ADDRESS, 0),
    )

    # 3. Unwrap ETH -> ETH
    calldata_unwrap_weth = cwrap.unwrapWrappedNative.encode_input("0.3 ether")

    # 4-6. Move ETH -> account 3,4,5
    calldata_move_eth_3 = cmove.moveNative.encode_input(accounts[3], "0.1 ether")
    calldata_move_eth_4 = cmove.moveNative.encode_input(accounts[4], "0.1 ether")
    calldata_move_eth_5 = cmove.moveNative.encode_input(accounts[5], "0.1 ether")

    account_3_starting_balance = accounts[3].balance()
    account_4_starting_balance = accounts[4].balance()
    account_5_starting_balance = accounts[5].balance()

    invoker.invoke(
        [
            cmove.address,
            cswap.address,
            cwrap.address,
            cmove.address,
            cmove.address,
            cmove.address,
        ],
        [
            calldata_move_dai,
            calldata_swap_dai_eth,
            calldata_unwrap_weth,
            calldata_move_eth_3,
            calldata_move_eth_4,
            calldata_move_eth_5,
        ],
        {"from": bob},
    )

    assert accounts[3].balance() == account_3_starting_balance + "0.1 ether"
    assert accounts[4].balance() == account_4_starting_balance + "0.1 ether"
    assert accounts[5].balance() == account_5_starting_balance + "0.1 ether"


def test_wrap_ether_in_multiple_transactions(invoker, alice, weth, cwrap, cmove):
    """
    This is a test that highlights how msg.value works in multiple delegatecalls
    Note that the total value attached to this transaction is 1.5 ether
    The first wrap will utilise 0.5 ether, leaving 1.0 ether on the invoker
    The second wrap will use the remaining 1.0 ether
    """

    starting_balance = alice.balance()
    starting_weth_balance = weth.balanceOf(alice)
    starting_invoker_weth_balance = weth.balanceOf(invoker)

    value_a = "1 ether"
    value_b = "0.5 ether"
    total_value = "1.5 ether"  # can't do string multiplication
    calldata_wrap_eth_a = cwrap.wrapNative.encode_input(value_a)
    calldata_move_weth = cmove.moveERC20Out.encode_input(weth.address, alice.address, value_a)
    calldata_wrap_eth_b = cwrap.wrapNative.encode_input(value_b)

    invoker.invoke(
        [cwrap.address, cmove.address, cwrap.address],
        [calldata_wrap_eth_a, calldata_move_weth, calldata_wrap_eth_b],
        {"from": alice, "value": total_value},
    )

    assert alice.balance() == starting_balance - total_value
    assert weth.balanceOf(alice) == starting_weth_balance + value_a
    assert weth.balanceOf(invoker) == starting_invoker_weth_balance + value_b


def test_wrap_ether_in_multiple_transactions_can_leave_eth_on_invoker(
    invoker, alice, weth, cwrap, cmove
):
    """
    This test is similar to the above test, however does not have the second wrap.
    If you follow the ether:
    1.5 ether is sent to the invoker via msg.value
    0.5 ether is used to wrap into weth
    At the end of invocation, 1 ether should remain on the invoker
    (in reality, this should be sweeped to user)
    """

    starting_balance = alice.balance()
    starting_weth_balance = weth.balanceOf(alice)
    starting_invoker_weth_balance = weth.balanceOf(invoker)
    starting_invoker_eth_balance = invoker.balance()

    value_a = "1 ether"
    value_b = "0.5 ether"
    total_value = "1.5 ether"  # can't do string multiplication
    calldata_wrap_eth_a = cwrap.wrapNative.encode_input(value_a)
    calldata_move_weth = cmove.moveERC20Out.encode_input(weth.address, alice.address, value_a)

    invoker.invoke(
        [cwrap.address, cmove.address],
        [calldata_wrap_eth_a, calldata_move_weth],
        {"from": alice, "value": total_value},
    )

    assert alice.balance() == starting_balance - total_value
    assert weth.balanceOf(alice) == starting_weth_balance + value_a
    assert invoker.balance() == starting_invoker_eth_balance + value_b
    assert weth.balanceOf(invoker) == starting_invoker_weth_balance


def test_wrap_ether_in_multiple_transactions_should_fail_with_no_ether_attached(
    invoker, alice, weth, cwrap, cmove
):
    """If we don't attach any ether to the above transactions, they should fail"""

    value_a = "1 ether"
    value_b = "0.5 ether"
    calldata_wrap_eth_a = cwrap.wrapNative.encode_input(value_a)
    calldata_move_weth = cmove.moveERC20Out.encode_input(weth.address, alice.address, value_a)
    calldata_wrap_eth_b = cwrap.wrapNative.encode_input(value_b)

    with reverts():
        invoker.invoke(
            [cwrap.address, cmove.address, cwrap.address],
            [calldata_wrap_eth_a, calldata_move_weth, calldata_wrap_eth_b],
            {"from": alice, "value": "0 ether"},  # emphasis on 0 ether
        )


def test_move_swap_then_sweep_rest(invoker, alice, bob, cswap, cwrap, dai, weth, cmove, uni_router):
    alice_starting_balance = alice.balance()
    bob_starting_balance = bob.balance()
    invoker_starting_balance = invoker.balance()

    alice_starting_dai_balance = dai.balanceOf(alice.address)
    bob_starting_dai_balance = dai.balanceOf(bob.address)

    value = "1 ether"

    # 1. Wrap ETH
    calldata_wrap_eth = cwrap.wrapNative.encode_input(value)

    # 2. Swap WETH -> Dai
    calldata_swap_weth_dai = cswap.sell.encode_input(
        value, weth, dai, 0, (uni_router, [weth, dai], ZERO_ADDRESS, 0)
    )

    # 3. Move Dai -> Bob
    calldata_move_dai = cmove.moveERC20Out.encode_input(dai.address, bob.address, 100 * 1e18)

    # 4. Sweep rest to Alice
    calldata_sweep_dai = cmove.moveAllERC20Out.encode_input(dai.address, alice.address)

    invoker.invoke(
        [cwrap.address, cswap.address, cmove.address, cmove.address],
        [calldata_wrap_eth, calldata_swap_weth_dai, calldata_move_dai, calldata_sweep_dai],
        {"from": alice, "value": "1 ether"},
    )

    assert alice.balance() == alice_starting_balance - "1 ether"
    assert bob.balance() == bob_starting_balance
    assert dai.balanceOf(alice.address) > alice_starting_dai_balance
    assert dai.balanceOf(bob.address) == bob_starting_dai_balance + "100 ether"
    assert invoker.balance() == invoker_starting_balance
    assert dai.balanceOf(invoker.address) == 0
