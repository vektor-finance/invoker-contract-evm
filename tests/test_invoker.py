import brownie
import pytest
from brownie import Invoker, accounts


@pytest.fixture(scope="module")
def invoker():
    return accounts[0].deploy(Invoker)


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_owner(invoker):
    assert invoker.hasRole("0x00", accounts[0])


def test_should_revert_if_unequal_length(invoker, dai):
    calldata_one = dai.transferFrom.encode_input(accounts[0], accounts[1], 1000)
    calldata_two = dai.transferFrom.encode_input(accounts[0], accounts[1], 1000)
    with brownie.reverts("dev: to+data length not equal"):
        invoker.invoke([dai.address], [calldata_one, calldata_two], {"from": accounts[0]})
