# Move and Swap
from helpers import get_dai_for_user

# ALICE wants to swap her ETH for DAI
# Invoke:
# 1. Wrap ETH -> WETH
# 2. Swap WETH -> DAI
# 3. Move DAI -> Alice


def test_swap_eth_for_dai(invoker, alice, cmove, cswap, weth, dai):
    value = "1 ether"
    starting_balance = alice.balance()

    # 1. Wrap ETH
    calldata_wrap_eth = cswap.wrapEth.encode_input(value)

    # 2. Swap WETH -> Dai
    calldata_swap_weth_dai = cswap.swapUniswapIn.encode_input(value, 0, [weth.address, dai.address])

    # 3. Move Dai -> Alice
    calldata_move_dai = cmove.moveERC20Out.encode_input(dai.address, alice.address, 100 * 1e18)

    invoker.invoke(
        [cswap.address, cswap.address, cmove.address],
        [calldata_wrap_eth, calldata_swap_weth_dai, calldata_move_dai],
        {"from": alice, "value": value},
    )

    assert alice.balance() == starting_balance - "1 ether"
    assert dai.balanceOf(alice) == 100 * 1e18


# Bob wants to quickly fund three accounts to farm airdrops
# First: Approve Dai on invoker
# Invoke:
# 1. Move Dai -> Invoker
# 2. Swap Dai -> WETH
# 3. Unrwap WETH -> ETH
# 4. Move ETH -> Account 3
# 5. Move ETH -> Account 4
# 6. Move ETH -> Account 5
# Note accounts 0,1,2 already reserved


def test_swap_dai_to_eth_and_disperse(invoker, bob, cmove, cswap, weth, dai, uni_router, accounts):
    # First get the user one eth worth of dai
    get_dai_for_user(dai, bob, weth, uni_router)

    dai.approve(invoker.address, 2000 * 1e18, {"from": bob.address})

    # 1. Move Dai to invoker
    calldata_move_dai = cmove.moveERC20In.encode_input(dai.address, 2000 * 1e18)

    # 2. Swap Dai -> WETH
    calldata_swap_dai_eth = cswap.swapUniswapOut.encode_input(
        "0.3 ether", 2000 * 1e18, [dai.address, weth.address]
    )

    # 3. Unwrap ETH -> ETH
    calldata_unwrap_eth = cswap.unwrapEth.encode_input("0.3 ether")

    # 4-6. Move ETH -> account 3,4,5
    calldata_move_eth_3 = cmove.moveEth.encode_input(accounts[3], "0.1 ether")
    calldata_move_eth_4 = cmove.moveEth.encode_input(accounts[4], "0.1 ether")
    calldata_move_eth_5 = cmove.moveEth.encode_input(accounts[5], "0.1 ether")

    account_3_starting_balance = accounts[3].balance()
    account_4_starting_balance = accounts[4].balance()
    account_5_starting_balance = accounts[5].balance()

    invoker.invoke(
        [cmove.address, cswap.address, cswap.address, cmove.address, cmove.address, cmove.address],
        [
            calldata_move_dai,
            calldata_swap_dai_eth,
            calldata_unwrap_eth,
            calldata_move_eth_3,
            calldata_move_eth_4,
            calldata_move_eth_5,
        ],
        {"from": bob},
    )

    assert accounts[3].balance() == account_3_starting_balance + "0.1 ether"
    assert accounts[4].balance() == account_4_starting_balance + "0.1 ether"
    assert accounts[5].balance() == account_5_starting_balance + "0.1 ether"
