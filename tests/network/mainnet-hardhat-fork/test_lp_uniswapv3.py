import brownie
import pytest
from brownie import ZERO_ADDRESS, interface

from data.access_control import APPROVED_COMMAND
from data.test_helpers import mint_tokens_for
from data.uniswapv3 import (
    get_amounts_for_liquidity,
    get_liquidity_for_amounts,
    get_sqrt_ratio_at_tick,
)

FULL_RANGE_LOWER_TICK = -887220
FULL_RANGE_UPPER_TICK = -FULL_RANGE_LOWER_TICK


@pytest.fixture(scope="module")
def clp_uniswapv3(invoker, deployer, CLPUniswapV3):
    interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")
    contract = deployer.deploy(CLPUniswapV3)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def position(invoker, clp_uniswapv3, alice, cmove, chain):
    nftm = interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")

    tick_lower = FULL_RANGE_LOWER_TICK
    tick_upper = FULL_RANGE_UPPER_TICK

    # WETH-USDC 0.3%
    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    usdc_amount = 100e6
    weth_amount = 0.05e18

    mint_tokens_for(usdc, alice, usdc_amount)
    mint_tokens_for(weth, alice, weth_amount)

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    sqrt_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    expected_liquidity = get_liquidity_for_amounts(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        usdc_amount,
        weth_amount,
    )
    min_usdc_used, min_weth_used = get_amounts_for_liquidity(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        int(expected_liquidity * 0.99),
    )

    calldata_deposit = clp_uniswapv3.depositNew.encode_input(
        uniswap_pool,
        tick_lower,
        tick_upper,
        usdc_amount,
        weth_amount,
        (nftm, min_usdc_used, min_weth_used, alice, chain.time() + 100),
    )

    calldata_sweep_usdc = cmove.moveAllERC20Out.encode_input(usdc, alice)
    calldata_sweep_weth = cmove.moveAllERC20Out.encode_input(weth, alice)

    tx = invoker.invoke(
        [cmove, cmove, clp_uniswapv3, cmove, cmove],
        [
            calldata_move_usdc,
            calldata_move_weth,
            calldata_deposit,
            calldata_sweep_usdc,
            calldata_sweep_weth,
        ],
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


@pytest.fixture(scope="module")
def nftm():
    yield interface.NonfungiblePositionManager("0xc36442b4a4522e871399cd717abdd847ab11fe88")


@pytest.mark.parametrize("receiver", ["user", ZERO_ADDRESS], ids=["alice", "zero address"])
def test_mint(nftm, receiver, cmove, chain, invoker, alice, clp_uniswapv3):
    if receiver == "user":
        receiver = alice
        target_receiver = alice
    else:
        target_receiver = invoker

    tick_lower = FULL_RANGE_LOWER_TICK
    tick_upper = FULL_RANGE_UPPER_TICK

    # WETH-USDC 0.3%
    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    usdc_amount = 100e6
    weth_amount = 0.05e18
    mint_tokens_for(usdc, alice, usdc_amount)
    mint_tokens_for(weth, alice, weth_amount)

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    sqrt_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    expected_liquidity = get_liquidity_for_amounts(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        usdc_amount,
        weth_amount,
    )
    min_usdc_used, min_weth_used = get_amounts_for_liquidity(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        int(expected_liquidity * 0.99),
    )

    calldata_deposit = clp_uniswapv3.depositNew.encode_input(
        uniswap_pool,
        tick_lower,
        tick_upper,
        usdc_amount,
        weth_amount,
        (nftm, min_usdc_used, min_weth_used, receiver, chain.time() + 100),
    )

    tx = invoker.invoke(
        [cmove, cmove, clp_uniswapv3],
        [
            calldata_move_usdc,
            calldata_move_weth,
            calldata_deposit,
        ],
        {"from": alice},
    )

    token_id = tx.events["IncreaseLiquidity"]["tokenId"]

    assert nftm.ownerOf(token_id) == target_receiver


def test_add_liquidity(position, nftm, alice, clp_uniswapv3, cmove, chain, invoker):

    initial_position = nftm.positions(position).dict()

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    tick_lower, tick_upper = FULL_RANGE_LOWER_TICK, FULL_RANGE_UPPER_TICK

    usdc_amount = 100e6
    weth_amount = 0.05e18

    mint_tokens_for(usdc, alice, usdc_amount)
    mint_tokens_for(weth, alice, weth_amount)

    usdc.approve(invoker, usdc_amount, {"from": alice})
    weth.approve(invoker, weth_amount, {"from": alice})

    calldata_move_usdc = cmove.moveERC20In.encode_input(usdc, usdc_amount)
    calldata_move_weth = cmove.moveERC20In.encode_input(weth, weth_amount)

    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    sqrt_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    expected_liquidity = get_liquidity_for_amounts(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        usdc_amount,
        weth_amount,
    )
    min_usdc_used, min_weth_used = get_amounts_for_liquidity(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        int(expected_liquidity * 0.99),
    )

    calldata_add = clp_uniswapv3.deposit.encode_input(
        position,
        usdc_amount,
        weth_amount,
        (nftm, min_usdc_used, min_weth_used, alice, chain.time() + 100),
    )

    invoker.invoke(
        [cmove, cmove, clp_uniswapv3],
        [calldata_move_usdc, calldata_move_weth, calldata_add],
        {"from": alice},
    )

    after_position = nftm.positions(position).dict()

    assert after_position["liquidity"] >= initial_position["liquidity"] + 0.99 * expected_liquidity


@pytest.mark.parametrize("receiver", ["user", ZERO_ADDRESS], ids=["alice", "zero address"])
def test_remove_some_liquidity(position, nftm, alice, invoker, clp_uniswapv3, chain, receiver):
    if receiver == "user":
        receiver = alice
        target_receiver = alice
    else:
        target_receiver = invoker

    initial_position = nftm.positions(position).dict()
    liquidity_to_remove = initial_position["liquidity"] // 3
    nftm.approve(invoker, position, {"from": alice})

    tick_lower, tick_upper = FULL_RANGE_LOWER_TICK, FULL_RANGE_UPPER_TICK

    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    sqrt_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    expected_usdc_received, expected_weth_received = get_amounts_for_liquidity(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        liquidity_to_remove,
    )

    calldata_remove = clp_uniswapv3.withdraw.encode_input(
        position,
        liquidity_to_remove,
        (
            nftm,
            0.99 * expected_usdc_received,
            0.99 * expected_weth_received,
            receiver,
            chain.time() + 100,
        ),
    )

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
    usdc_start_balance = usdc.balanceOf(target_receiver)
    weth_start_balance = weth.balanceOf(target_receiver)

    tx = invoker.invoke([clp_uniswapv3], [calldata_remove], {"from": alice})

    after_position = nftm.positions(position).dict()

    assert "DecreaseLiquidity" in tx.events
    assert (
        initial_position["liquidity"]
        == after_position["liquidity"] + tx.events["DecreaseLiquidity"]["liquidity"]
    )
    assert usdc.balanceOf(target_receiver) == usdc_start_balance + tx.events["Transfer"][0]["value"]
    assert weth.balanceOf(target_receiver) == weth_start_balance + tx.events["Transfer"][1]["value"]


def test_fail_remove_some_liquidity_invalid_user(
    position, nftm, alice, bob, invoker, clp_uniswapv3, chain
):
    initial_position = nftm.positions(position).dict()
    liquidity_to_remove = initial_position["liquidity"] // 3
    nftm.approve(invoker, position, {"from": alice})

    calldata_remove = clp_uniswapv3.withdraw.encode_input(
        position, liquidity_to_remove, (nftm, 0, 0, alice, chain.time() + 100)
    )

    with brownie.reverts("CLPUniswapV3:not your position"):
        invoker.invoke([clp_uniswapv3], [calldata_remove], {"from": bob})


@pytest.mark.parametrize("receiver", ["user", ZERO_ADDRESS], ids=["alice", "zero address"])
def test_remove_all_liquidity(position, nftm, alice, invoker, clp_uniswapv3, chain, receiver):
    if receiver == "user":
        receiver = alice
        target_receiver = alice
    else:
        target_receiver = invoker

    nftm.approve(invoker, position, {"from": alice})
    initial_position = nftm.positions(position).dict()
    liquidity_to_remove = initial_position["liquidity"]

    tick_lower, tick_upper = FULL_RANGE_LOWER_TICK, FULL_RANGE_UPPER_TICK

    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    usdc_start_balance = usdc.balanceOf(target_receiver)
    weth_start_balance = weth.balanceOf(target_receiver)

    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    sqrt_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    expected_usdc_received, expected_weth_received = get_amounts_for_liquidity(
        sqrt_price,
        get_sqrt_ratio_at_tick(tick_lower),
        get_sqrt_ratio_at_tick(tick_upper),
        liquidity_to_remove,
    )
    calldata_remove_all = clp_uniswapv3.withdrawAll.encode_input(
        position,
        (
            nftm,
            0.99 * expected_usdc_received,
            0.99 * expected_weth_received,
            receiver,
            chain.time() + 100,
        ),
    )
    tx = invoker.invoke([clp_uniswapv3], [calldata_remove_all], {"from": alice})

    # reverts after token is burnt
    with brownie.reverts("Invalid token ID"):
        nftm.positions(position)

    assert "DecreaseLiquidity" in tx.events
    assert "Burn" in tx.events

    assert (
        usdc.balanceOf(target_receiver) == usdc_start_balance + tx.events["Transfer"][0]["value"]
        and weth.balanceOf(target_receiver)
        == weth_start_balance + tx.events["Transfer"][1]["value"]
    )


def test_fail_remove_all_liquidity_invalid_user(
    position, nftm, alice, bob, invoker, chain, clp_uniswapv3
):
    nftm.approve(invoker, position, {"from": alice})

    calldata_remove_all = clp_uniswapv3.withdrawAll.encode_input(
        position, (nftm, 0, 0, alice, chain.time() + 100)
    )
    with brownie.reverts("CLPUniswapV3:not your position"):
        invoker.invoke([clp_uniswapv3], [calldata_remove_all], {"from": bob})


@pytest.mark.parametrize("receiver", ["user", ZERO_ADDRESS], ids=["alice", "zero address"])
def test_collect(position, alice, bob, clp_uniswapv3, invoker, chain, nftm, receiver):
    if receiver == "user":
        receiver = alice
    usdc = interface.ERC20Detailed("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    weth = interface.ERC20Detailed("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    bob_usdc_amount = usdc.balanceOf(alice)
    bob_weth_amount = weth.balanceOf(alice)
    usdc.transfer(bob, bob_usdc_amount, {"from": alice})
    weth.transfer(bob, bob_weth_amount, {"from": alice})

    router = interface.UniswapV3SwapRouter("0xE592427A0AEce92De3Edee1F18E0157C05861564")
    uniswap_pool = interface.UniswapV3Pool("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")

    # Execute a trade on the pool, generating fees for alice (in USDC)
    initial_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    usdc.approve(router, bob_usdc_amount, {"from": bob})
    deadline = chain.time() + 100
    router.exactInputSingle((usdc, weth, 3000, bob, deadline, bob_usdc_amount, 0, 0), {"from": bob})
    final_price = uniswap_pool.slot0().dict()["sqrtPriceX96"]
    assert final_price < initial_price

    calldata_collect = clp_uniswapv3.collectAll.encode_input(nftm, position, receiver)

    nftm.approve(invoker, position, {"from": alice})

    if receiver == ZERO_ADDRESS:
        target_receiver = invoker
    else:
        target_receiver = alice

    starting_balance = usdc.balanceOf(target_receiver)

    tx = invoker.invoke(
        [clp_uniswapv3],
        [calldata_collect],
        {"from": alice},
    )

    collect_event = tx.events["Collect"]

    assert collect_event["amount0"] == usdc.balanceOf(target_receiver) - starting_balance


def test_fail_collect_invalid_user(position, nftm, alice, bob, invoker, clp_uniswapv3, chain):
    nftm.approve(invoker, position, {"from": alice})

    calldata_collect = clp_uniswapv3.collectAll.encode_input(nftm, position, bob)

    with brownie.reverts("CLPUniswapV3:not your position"):
        invoker.invoke([clp_uniswapv3], [calldata_collect], {"from": bob})
