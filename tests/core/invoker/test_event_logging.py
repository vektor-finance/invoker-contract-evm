def test_is_event_logged_log_invocation_on_invoke(invoker, alice, bob, cmove):
    calldata_transfer_one_eth = cmove.moveNative.encode_input(bob.address, "1 ether")

    tx = invoker.invoke(
        [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
    )

    events = tx.events
    assert "LogInvocation" in events
    event = events["LogInvocation"]
    assert event["user"] == alice.address
    assert event["sigHash"] == "0x567b3a1b"  # Function selector for invoke(address[],bytes[])
    assert event["params"] == tx.input
    assert event["value"] == "1 ether"


def test_is_event_logged_single_log_vek_on_invoke(invoker, alice, bob, cmove):
    calldata_transfer_one_eth = cmove.moveNative.encode_input(bob.address, "1 ether")

    tx = invoker.invoke(
        [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
    )

    events = tx.events
    assert "LogStep" in events
    event = events["LogStep"]
    assert event["user"] == alice.address
    assert event["sigHash"] == "0x71096cbb"  # Function selector for moveNative(address,uint256)
    assert event["params"] == calldata_transfer_one_eth


def test_is_event_logged_multiple_log_veks_on_invoke(invoker, alice, bob, mock_erc20, cmove):
    value = "1 ether"
    mock_erc20.mint(alice, value, {"from": alice})
    mock_erc20.approve(invoker.address, value, {"from": alice})
    fn_move_in = cmove.moveERC20In["address,uint256"]
    fn_move_out = cmove.moveERC20Out["address,address,uint256"]
    calldata_move_erc20_in = fn_move_in.encode_input(mock_erc20.address, value)
    calldata_move_erc20_out = fn_move_out.encode_input(mock_erc20.address, bob.address, value)

    tx = invoker.invoke(
        [cmove.address, cmove.address],
        [calldata_move_erc20_in, calldata_move_erc20_out],
        {"from": alice},
    )
    events = tx.events
    assert "LogStep" in events
    assert len(events["LogStep"]) == 2
    ev0 = events["LogStep"][0]
    ev1 = events["LogStep"][1]
    # Check first event
    assert ev0["user"] == alice.address
    assert ev0["sigHash"] == fn_move_in.signature
    assert ev0["params"] == calldata_move_erc20_in
    # Check second event
    assert ev1["user"] == alice.address
    assert ev1["sigHash"] == fn_move_out.signature
    assert ev1["params"] == calldata_move_erc20_out
