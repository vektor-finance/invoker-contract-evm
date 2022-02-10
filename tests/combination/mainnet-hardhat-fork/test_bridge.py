import time

import pytest
from brownie import Contract

from data.access_control import APPROVED_COMMAND


@pytest.fixture
def cbridge(deployer, invoker, CBridge, weth):
    contract = deployer.deploy(CBridge, weth, "0x6b7a87899490EcE95443e979cA9485CBE7E71522")
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract


@pytest.fixture
def anyswaprouter(interface, autouse=True):
    # this is a hack to get the anyswap router into memory -> allows for event logging
    Contract.from_abi(
        "ANYSWAP ROUTER",
        "0x6b7a87899490EcE95443e979cA9485CBE7E71522",
        interface.AnyswapV5Router.abi,
    )


# def test_native_bridge(cbridge, alice, invoker, bob):
#     amount = 100
#     calldata_bridge_native = cbridge.bridgeNative.encode_input(amount, bob, 4)
#     invoker.invoke([cbridge.address], [calldata_bridge_native], {"from": alice, "value": amount})


def test_erc20_bridge(cbridge, cmove, alice, invoker, bob, weth, uni_router, interface):
    token = Contract.from_abi(
        "TOKEN", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", interface.IERC20.abi
    )
    anytoken = Contract.from_abi(
        "ANYTOKEN", "0x7ea2be2df7ba6e54b1a9c70676f668455e329d29", interface.IERC20.abi
    )
    path = [weth.address, token.address]
    uni_router.swapExactETHForTokens(
        0, path, alice, time.time() + 1, {"from": alice, "value": 1e18}
    )
    amount = token.balanceOf(alice)

    calldata_move_in = cmove.moveERC20In.encode_input(token.address, amount)

    calldata_bridge_native = cbridge.bridgeERC20.encode_input(
        token.address, anytoken.address, amount, bob, 4
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
    assert evt["toChainID"] == 4
