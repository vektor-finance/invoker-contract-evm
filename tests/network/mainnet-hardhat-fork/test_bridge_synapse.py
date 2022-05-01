import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND

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
