import pytest
from brownie import ZERO_ADDRESS, Contract
from brownie.exceptions import VirtualMachineError


@pytest.mark.dedupe("tokens_for_alice", "token")
def test_sell_invoker(tokens_for_alice, token, uni_router, alice, cmove, cswap, invoker, interface):
    amount_in = tokens_for_alice.balanceOf(alice)
    path = [tokens_for_alice, token]
    try:
        (_, amount_out) = uni_router.getAmountsOut(amount_in, path)
    except VirtualMachineError:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    if amount_out == 0:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    tokens_for_alice.approve(invoker, amount_in, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice, amount_in)
    calldata_sell = cswap.sell.encode_input(
        amount_in, amount_out, path, (uni_router, path, ZERO_ADDRESS, 0)
    )
    calldata_move_out = cmove.moveAllERC20Out.encode_input(token, alice)

    try:
        invoker.invoke(
            [cmove, cswap, cmove],
            [calldata_move_in, calldata_sell, calldata_move_out],
            {"from": alice},
        )
    except VirtualMachineError:
        """On some chains, the uniswap pair may not be in sync.
        We must manually sync it before executing the trade."""
        factory = Contract.from_abi(
            f"{uni_router._name} Factory", uni_router.factory(), interface.UniswapV2Factory.abi
        )
        pair = Contract.from_abi(
            f"{uni_router._name} Pair",
            factory.getPair(tokens_for_alice, token),
            interface.UniswapV2Pair.abi,
        )
        pair.sync({"from": alice})

        (_, amount_out) = uni_router.getAmountsOut(amount_in, path)
        calldata_sell = cswap.sell.encode_input(
            amount_in, amount_out, path, (uni_router, path, ZERO_ADDRESS, 0)
        )

        invoker.invoke(
            [cmove, cswap, cmove],
            [calldata_move_in, calldata_sell, calldata_move_out],
            {"from": alice},
        )

    assert token.balanceOf(alice) >= amount_out


@pytest.mark.dedupe("tokens_for_alice", "token")
def test_buy_invoker(tokens_for_alice, token, uni_router, alice, cmove, cswap, invoker, interface):
    # We have minted 100 tokens for alice.
    # We need to pick an amount to buy that we know alice can afford
    starting_balance = tokens_for_alice.balanceOf(alice)
    path = [tokens_for_alice, token]
    try:
        (_, amount_out) = uni_router.getAmountsOut(starting_balance, path)
    except VirtualMachineError:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    if amount_out == 0:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    # Spend half of alices tokens buying
    amount_out //= 2

    try:
        (amount_in, _) = uni_router.getAmountsIn(amount_out, path)
    except VirtualMachineError:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    tokens_for_alice.approve(invoker, amount_in, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice, amount_in)
    calldata_buy = cswap.buy.encode_input(
        amount_out, amount_in, path, (uni_router, path, ZERO_ADDRESS, 0)
    )
    calldata_sweep_input = cmove.moveAllERC20Out.encode_input(tokens_for_alice, alice)
    calldata_move_out = cmove.moveERC20Out.encode_input(token, alice, amount_out)
    try:
        invoker.invoke(
            [cmove, cswap, cmove, cmove],
            [calldata_move_in, calldata_buy, calldata_sweep_input, calldata_move_out],
            {"from": alice},
        )
    except VirtualMachineError:
        """On some chains, the uniswap pair may not be in sync.
        We must manually sync it before executing the trade."""

        factory = Contract.from_abi(
            f"{uni_router._name} Factory", uni_router.factory(), interface.UniswapV2Factory.abi
        )
        pair = Contract.from_abi(
            f"{uni_router._name} Pair",
            factory.getPair(tokens_for_alice, token),
            interface.UniswapV2Pair.abi,
        )
        pair.sync({"from": alice})

        (amount_in, _) = uni_router.getAmountsIn(amount_out, path)
        calldata_buy = cswap.buy.encode_input(
            amount_out, amount_in, path, (uni_router, path, ZERO_ADDRESS, 0)
        )
        tokens_for_alice.approve(invoker, 0, {"from": alice})
        tokens_for_alice.approve(invoker, amount_in, {"from": alice})

        invoker.invoke(
            [cmove, cswap, cmove, cmove],
            [calldata_move_in, calldata_buy, calldata_sweep_input, calldata_move_out],
            {"from": alice},
        )

    assert starting_balance - tokens_for_alice.balanceOf(alice) <= amount_in
    assert token.balanceOf(alice) >= amount_out
