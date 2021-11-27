import pytest


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


"""
calldata_transfer_one_eth = cmove.moveEth.encode_input(bob.address, "1 ether")
0x1cc1472d      The function selector for moveEth()
0000000000000000000000003c44cdddb6a900fa2b585dd299e03d12fa4293bc
0000000000000000000000000000000000000000000000000de0b6b3a7640000
"""

"""
tx = invoker.invoke(
    [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
)
0x567b3a1b      The function selector for invoke(address[],bytes[])
0000000000000000000000000000000000000000000000000000000000000040    Position of first variable
0000000000000000000000000000000000000000000000000000000000000080    Position of second variable
0000000000000000000000000000000000000000000000000000000000000001    Length of first array
000000000000000000000000fbc22278a96299d91d41c453234d97b4f5eb9b2d    First address
0000000000000000000000000000000000000000000000000000000000000001    Length of second array
0000000000000000000000000000000000000000000000000000000000000020
0000000000000000000000000000000000000000000000000000000000000044
1cc1472d0000000000000000000000003c44cdddb6a900fa2b585dd299e03d12    Calldata (1)
fa4293bc0000000000000000000000000000000000000000000000000de0b6b3    Calldata (2)
a764000000000000000000000000000000000000000000000000000000000000    Calldata (3)
"""


def test_event_logged_on_invoke(invoker, alice, bob, cmove):
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


def test_event_logged_veks_on_invoke(invoker, alice, bob, cmove):
    calldata_transfer_one_eth = cmove.moveEth.encode_input(bob.address, "1 ether")

    tx = invoker.invoke(
        [cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": "1 ether"}
    )

    events = tx.events
    assert "LogVeks" in events
    event = events["LogVeks"]
    assert event["user"] == alice.address
    assert event["sigHash"] == "0x1cc1472d"  # Function selector for moveEth()
    assert event["params"] == calldata_transfer_one_eth
    assert event["value"] == "1 ether"
