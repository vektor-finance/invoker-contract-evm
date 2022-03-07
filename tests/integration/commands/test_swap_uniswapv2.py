import pytest
from brownie import ZERO_ADDRESS, Contract, accounts, interface
from brownie.exceptions import VirtualMachineError


def sync(uni_router, token0, token1):
    factory = Contract.from_abi(
        f"{uni_router._name} Factory", uni_router.factory(), interface.UniswapV2Factory.abi
    )

    pair_addr = factory.getPair(token0, token1)

    if pair_addr != ZERO_ADDRESS:
        pair = Contract.from_abi(
            f"{uni_router._name} Pair",
            pair_addr,
            interface.UniswapV2Pair.abi,
        )
        pair.sync({"from": accounts[0]})


@pytest.mark.dedupe("tokens_for_alice", "token")
def test_sell_invoker(tokens_for_alice, token, uni_router, alice, cmove, cswap, invoker, interface):
    amount_in = tokens_for_alice.balanceOf(alice)
    path = [tokens_for_alice, token]
    try:
        sync(uni_router, tokens_for_alice, token)
        (_, amount_out) = uni_router.getAmountsOut(amount_in, path)
    except VirtualMachineError:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    if amount_out == 0:
        pytest.skip(f"No liquidity for {tokens_for_alice._name} -> {token._name}")

    tokens_for_alice.approve(invoker, amount_in, {"from": alice})

    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice, amount_in)
    calldata_sell = cswap.sell.encode_input(
        amount_in, tokens_for_alice, token, amount_out, (uni_router, path, ZERO_ADDRESS, 0)
    )
    calldata_move_out = cmove.moveAllERC20Out.encode_input(token, alice)

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
        sync(uni_router, tokens_for_alice, token)
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
        amount_out, token, tokens_for_alice, amount_in, (uni_router, path, ZERO_ADDRESS, 0)
    )
    calldata_sweep_input = cmove.moveAllERC20Out.encode_input(tokens_for_alice, alice)
    calldata_move_out = cmove.moveERC20Out.encode_input(token, alice, amount_out)
    invoker.invoke(
        [cmove, cswap, cmove, cmove],
        [calldata_move_in, calldata_buy, calldata_sweep_input, calldata_move_out],
        {"from": alice},
    )

    assert starting_balance - tokens_for_alice.balanceOf(alice) <= amount_in
    assert token.balanceOf(alice) >= amount_out
