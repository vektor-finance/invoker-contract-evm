# Move and Swap


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
