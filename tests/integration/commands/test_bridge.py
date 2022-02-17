import pytest


def test_native_bridge(cbridge, alice, any_native_token, anyswap_router_v4, invoker, bob):
    if any_native_token["router"] != anyswap_router_v4.address.lower():
        pytest.skip("Testing incorrect router for token")
    amount = 100
    calldata_bridge_native = cbridge.bridgeNative.encode_input(amount, bob, 4)
    tx = invoker.invoke(
        [cbridge.address], [calldata_bridge_native], {"from": alice, "value": amount}
    )
    assert "LogAnySwapOut" in tx.events
    evt = tx.events["LogAnySwapOut"]
    assert evt["token"] == any_native_token["address"]
    assert evt["from"] == invoker.address
    assert evt["to"] == bob.address
    assert evt["amount"] == amount
    assert evt["fromChainID"] == 1337
    assert evt["toChainID"] == 4


def test_erc20_bridge(
    cbridge,
    cmove,
    alice,
    invoker,
    bob,
    mint_anyswap_token_v4,
    anyswap_router_v4,
    anyswap_token_dest_chain,
):
    if mint_anyswap_token_v4["router"] != anyswap_router_v4.address.lower():
        pytest.skip("Testing incorrect router for token")
    token = mint_anyswap_token_v4["underlying"]
    anytoken = mint_anyswap_token_v4["anyToken"]

    amount = token.balanceOf(alice)

    calldata_move_in = cmove.moveERC20In.encode_input(token.address, amount)

    calldata_bridge_native = cbridge.bridgeERC20.encode_input(
        token.address, anytoken.address, amount, bob, anyswap_token_dest_chain
    )

    token.approve(invoker.address, amount, {"from": alice})
    tx = invoker.invoke(
        [cmove.address, cbridge.address],
        [calldata_move_in, calldata_bridge_native],
        {"from": alice},
    )
    assert "LogAnySwapOut" in tx.events
    evt = tx.events["LogAnySwapOut"]
    assert evt["token"] == anytoken.address
    assert evt["from"] == invoker
    assert evt["to"] == bob
    assert evt["fromChainID"] == 1337
    assert evt["toChainID"] == anyswap_token_dest_chain
    assert evt["amount"] == amount
