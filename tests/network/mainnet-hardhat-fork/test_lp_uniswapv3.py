import math

import brownie
import pytest
from brownie import interface

from data.access_control import APPROVED_COMMAND
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def clp_uniswapv3(invoker, deployer, CLPUniswapV3):
    interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    contract = deployer.deploy(CLPUniswapV3)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def position(invoker, clp_uniswapv3, alice, cmove, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")

    tick_lower = 0
    tick_upper = 6000

    # WETH-USDC 0.3%
    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    mint_tokens_for(usdc, alice)
    mint_tokens_for(weth, alice)

    usdc_amount = 100e6
    weth_amount = 0.05e18

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    calldata_deposit = clp_uniswapv3.depositNew.encode_input(
        uniswap_pool,
        tick_lower,
        tick_upper,
        usdc_amount,
        weth_amount,
        # todo: add slippage
        (nftm, 0, 0, alice, chain.time() + 100),
    )

    tx = invoker.invoke(
        [cmove, cmove, clp_uniswapv3],
        [calldata_move_usdc, calldata_move_weth, calldata_deposit],
        {"from": alice},
    )

    assert "Mint" in tx.events
    assert "IncreaseLiquidity" in tx.events
    token_id = tx.events["IncreaseLiquidity"]["tokenId"]

    position = nftm.positions(token_id).dict()
    assert position["token0"] == usdc
    assert position["token1"] == weth
    assert position["fee"] == 3000
    assert position["tickLower"] == tick_lower
    assert position["tickUpper"] == tick_upper

    assert nftm.ownerOf(token_id) == alice

    yield token_id


def test_mint(position):
    pass


Q96 = 0x1000000000000000000000000


def get_sqrt_ratio_at_tick(tick):
    return math.sqrt(1.0001**tick) * Q96


def get_liquidity_for_amount0(sqrt_ratioA, sqrt_ratioB, amount0):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    intermediate = sqrt_ratioA * sqrt_ratioB / Q96
    return amount0 * intermediate / (sqrt_ratioB - sqrt_ratioA)


def get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratioB, amount1):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)
    return amount1 * Q96 / (sqrt_ratioB - sqrt_ratioA)


def get_liquidity_for_amounts(sqrt_ratio, sqrt_ratioA, sqrt_ratioB, amount0, amount1):
    if sqrt_ratioA > sqrt_ratioB:
        sqrt_ratioA, sqrt_ratioB = (sqrt_ratioB, sqrt_ratioA)

    if sqrt_ratio <= sqrt_ratioA:
        liquidity = get_liquidity_for_amount0(sqrt_ratioA, sqrt_ratioB, amount0)
    elif sqrt_ratio < sqrt_ratioB:
        liquidity0 = get_liquidity_for_amount0(sqrt_ratio, sqrt_ratioB, amount0)
        liquidity1 = get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratio, amount1)
        liquidity = liquidity0 if liquidity0 < liquidity1 else liquidity1
    else:
        liquidity = get_liquidity_for_amount1(sqrt_ratioA, sqrt_ratioB, amount1)

    return liquidity


def test_add_liquidity(position, alice, clp_uniswapv3, cmove, chain, invoker):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")

    initial_position = nftm.positions(position).dict()

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    usdc_amount = 100e6
    weth_amount = 0.05e18

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    calldata_add = clp_uniswapv3.deposit.encode_input(
        position, usdc_amount, weth_amount, (nftm, 0, 0, alice, chain.time() + 100)
    )

    invoker.invoke(
        [cmove, cmove, clp_uniswapv3],
        [calldata_move_usdc, calldata_move_weth, calldata_add],
        {"from": alice},
    )

    after_position = nftm.positions(position).dict()

    # todo: calculate slippage
    assert after_position["liquidity"] > initial_position["liquidity"]
    assert False


def test_remove_some_liquidity(position, alice, invoker, clp_uniswapv3, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    initial_position = nftm.positions(position).dict()
    liquidity_to_remove = initial_position["liquidity"] // 3
    nftm.setApprovalForAll(invoker, True, {"from": alice})

    # todo: calculate slippage
    calldata_remove = clp_uniswapv3.withdraw.encode_input(
        position, liquidity_to_remove, (nftm, 0, 0, alice, chain.time() + 100)
    )

    tx = invoker.invoke([clp_uniswapv3], [calldata_remove], {"from": alice})

    after_position = nftm.positions(position).dict()

    assert "DecreaseLiquidity" in tx.events
    assert (
        initial_position["liquidity"]
        == after_position["liquidity"] + tx.events["DecreaseLiquidity"]["liquidity"]
    )


def test_fail_other_remove_some_liquidity(position, alice, bob, invoker, clp_uniswapv3, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    initial_position = nftm.positions(position).dict()
    liquidity_to_remove = initial_position["liquidity"] // 3
    nftm.setApprovalForAll(invoker, True, {"from": alice})

    calldata_remove = clp_uniswapv3.withdraw.encode_input(
        position, liquidity_to_remove, (nftm, 0, 0, alice, chain.time() + 100)
    )

    with brownie.reverts("CLPUniswapV3:not your position"):
        invoker.invoke([clp_uniswapv3], [calldata_remove], {"from": bob})


def test_remove_all_liquidity(position, alice, invoker, clp_uniswapv3, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    nftm.setApprovalForAll(invoker, True, {"from": alice})

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    usdc_start_balance = usdc.balanceOf(alice)
    weth_start_balance = weth.balanceOf(alice)

    # todo: calculate slippage
    calldata_remove_all = clp_uniswapv3.withdrawAll.encode_input(
        position,
        (nftm, 0, 0, alice, chain.time() + 100),
    )
    tx = invoker.invoke([clp_uniswapv3], [calldata_remove_all], {"from": alice})

    # reverts after token is burnt
    with brownie.reverts("Invalid token ID"):
        nftm.positions(position)

    assert "DecreaseLiquidity" in tx.events
    assert "Burn" in tx.events

    assert usdc.balanceOf(alice) > usdc_start_balance or weth.balanceOf(alice) > weth_start_balance


def test_fail_remove_all_liquidity(position, alice, bob, invoker, chain, clp_uniswapv3):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    nftm.setApprovalForAll(invoker, True, {"from": alice})

    calldata_remove_all = clp_uniswapv3.withdrawAll.encode_input(
        position, (nftm, 0, 0, alice, chain.time() + 100)
    )
    with brownie.reverts("CLPUniswapV3:not your position"):
        invoker.invoke([clp_uniswapv3], [calldata_remove_all], {"from": bob})
