import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND
from data.chain import get_chain, get_wnative_address
from data.test_helpers import mint_tokens_for


@pytest.fixture(scope="module")
def synapse_bridge():
    chain = get_chain()
    bridge = [
        contract
        for contract in chain["contracts"]
        if "synapse_bridge" in contract.get("interfaces")
    ]
    if len(bridge) > 0:
        return bridge[0]["address"]
    else:
        pytest.skip("Synapse not on this chain")


@pytest.fixture(scope="module")
def cbridge_synapse(invoker, deployer, CBridgeSynapse, connected_chain, synapse_bridge):
    wnative = get_wnative_address(connected_chain)
    contract = deployer.deploy(CBridgeSynapse, wnative, synapse_bridge)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    # to load abi
    Contract.from_abi("SynapseBridge", synapse_bridge, interface.SynapseBridge.abi)
    yield contract


def test_bridge_native(cbridge_synapse, invoker, alice, connected_chain):
    wnative = get_wnative_address(connected_chain)
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
    assert evt["token"] == wnative
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
