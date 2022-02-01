import pytest


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_is_event_logged_log_invocation_on_invoke(invoker, alice, bob, cmove):
    calldata_transfer_one_eth = cmove.moveEth.encode_input(bob.address, "1 ether")

    tx = invoker.invoke(
        [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
    )

    events = tx.events
    assert "LogInvocation" in events
    event = events["LogInvocation"]
    assert event["user"] == alice.address
    assert event["sigHash"] == "0x567b3a1b"  # Function selector for invoke()
    assert event["params"] == tx.input
    assert event["value"] == "1 ether"


def test_is_event_logged_single_log_vek_on_invoke(invoker, alice, bob, cmove):
    calldata_transfer_one_eth = cmove.moveEth.encode_input(bob.address, "1 ether")

    tx = invoker.invoke(
        [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
    )

    events = tx.events
    assert "LogStep" in events
    event = events["LogStep"]
    assert event["user"] == alice.address
    assert event["sigHash"] == "0x1cc1472d"  # Function selector for moveEth()
    assert event["params"] == calldata_transfer_one_eth


def test_is_event_logged_multiple_log_veks_on_invoke(invoker, alice, bob, weth, cmove, cswap):
    value = "1 ether"
    calldata_wrap_eth = cswap.wrapEth.encode_input(value)
    calldata_move_weth = cmove.moveERC20Out.encode_input(weth.address, bob.address, value)

    tx = invoker.invoke(
        [cswap.address, cmove.address],
        [calldata_wrap_eth, calldata_move_weth],
        {"from": alice, "value": value},
    )
    events = tx.events
    assert "LogStep" in events
    assert len(events["LogStep"]) == 2
    ev0 = events["LogStep"][0]
    ev1 = events["LogStep"][1]
    # Check first event
    assert ev0["user"] == alice.address
    assert ev0["sigHash"] == "0xae9779c6"  # Function selector for wrapEth(uint256)
    assert ev0["params"] == calldata_wrap_eth
    # Check second event
    assert ev1["user"] == alice.address
    assert (
        ev1["sigHash"] == "0x7f914ce0"
    )  # Function selector for moveERC20Out(address,address,uint256)
    assert ev1["params"] == calldata_move_weth
