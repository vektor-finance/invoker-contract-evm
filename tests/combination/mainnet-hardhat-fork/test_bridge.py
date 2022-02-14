import time

import pytest

from data.access_control import APPROVED_COMMAND


@pytest.fixture
def cbridge(deployer, invoker, CBridge, anyswap_router_v4, weth):
    contract = deployer.deploy(
        CBridge, weth, "0xB153FB3d196A8eB25522705560ac152eeEc57901", anyswap_router_v4.address
    )
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract


def test_native_bridge(cbridge, alice, invoker, bob):
    amount = 100
    calldata_bridge_native = cbridge.bridgeNative.encode_input(amount, bob, 4)
    tx = invoker.invoke(
        [cbridge.address], [calldata_bridge_native], {"from": alice, "value": amount}
    )
    assert "LogAnySwapOut" in tx.events
    evt = tx.events["LogAnySwapOut"]
    assert evt["token"] == "0xB153FB3d196A8eB25522705560ac152eeEc57901"
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
    weth,
    uni_router,
    anyswap_token_v4,
    anyswap_router_v4,
    anyswap_token_dest_chain,
):
    if anyswap_token_v4["router"] != anyswap_router_v4.address.lower():
        pytest.skip("Testing incorrect router for token")
    token = anyswap_token_v4["underlying"]
    anytoken = anyswap_token_v4["anyToken"]

    path = [weth.address, token.address]
    uni_router.swapExactETHForTokens(
        0, path, alice, time.time() + 1, {"from": alice, "value": 1e18}
    )
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
