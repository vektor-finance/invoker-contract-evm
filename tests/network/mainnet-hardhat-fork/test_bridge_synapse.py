import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND
from data.test_helpers import mint_tokens_for

WETH_ADDRESS = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
SYNAPSE_BRIDGE = "0x31fe393815822edacbd81c2262467402199efd0d"


@pytest.fixture(scope="module")
def cbridge_synapse(invoker, deployer, CBridgeSynapse):
    contract = deployer.deploy(CBridgeSynapse, WETH_ADDRESS, SYNAPSE_BRIDGE)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    # to load abi
    Contract.from_abi("SynapseBridge", SYNAPSE_BRIDGE, interface.SynapseBridge.abi)
    yield contract


def test_bridge_native(cbridge_synapse, invoker, alice):
    AMOUNT = 100
    DEST_CHAIN_ID = 1
    calldata_bridge_native = cbridge_synapse.bridgeNative.encode_input(
        AMOUNT, alice.address, DEST_CHAIN_ID
    )
    tx = invoker.invoke(
        [cbridge_synapse.address], [calldata_bridge_native], {"from": alice, "value": AMOUNT}
    )
    assert "TokenDeposit" in tx.events
    evt = tx.events["TokenDeposit"]
    assert evt["to"] == alice
    assert evt["chainId"] == DEST_CHAIN_ID
    assert evt["token"] == WETH_ADDRESS
    assert evt["amount"] == AMOUNT


@pytest.fixture(scope="module")
def nUSD():
    yield Contract.from_abi(
        "nUSD", "0x1b84765de8b7566e4ceaf4d0fd3c5af52d3dde4f", interface.ERC20Detailed.abi
    )


def test_bridge_erc20(cbridge_synapse, invoker, alice, cmove, nUSD):
    mint_tokens_for(nUSD, alice)
    AMOUNT = 100
    DEST_CHAIN_ID = 1
    calldata_bridge_erc20 = cbridge_synapse.bridgeERC20.encode_input(
        nUSD.address, AMOUNT, alice.address, DEST_CHAIN_ID
    )
    calldata_move_in = cmove.moveERC20In.encode_input(nUSD.address, AMOUNT)

    nUSD.approve(invoker, AMOUNT, {"from": alice})

    tx = invoker.invoke(
        [cmove.address, cbridge_synapse.address],
        [calldata_move_in, calldata_bridge_erc20],
        {"from": alice},
    )
    assert "TokenDeposit" in tx.events
    evt = tx.events["TokenDeposit"]
    assert evt["to"] == alice
    assert evt["chainId"] == DEST_CHAIN_ID
    assert evt["token"] == nUSD.address
    assert evt["amount"] == AMOUNT
