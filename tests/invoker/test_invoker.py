import brownie
import pytest


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_owner(invoker, deployer):
    assert invoker.hasRole("0x00", deployer)


def test_should_revert_if_unequal_length(invoker, dai, alice, bob):
    calldata_one = dai.transferFrom.encode_input(alice, bob, 1000)
    calldata_two = dai.transferFrom.encode_input(alice, bob, 1000)
    with brownie.reverts("dev: to+data length not equal"):
        invoker.invoke([dai.address], [calldata_one, calldata_two], {"from": alice})
