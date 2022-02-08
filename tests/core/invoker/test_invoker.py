import brownie
import pytest

from tests.helpers import get_dai_for_user


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


def test_cannot_invoke_when_contract_paused(invoker, deployer, alice, dai, weth, uni_router, cmove):
    invoker.pause({"from": deployer})
    get_dai_for_user(dai, alice, weth, uni_router)
    calldata = cmove.moveERC20In.encode_input(dai.address, 100 * 1e18)
    with brownie.reverts("PAC: Paused"):
        invoker.invoke([cmove.address], [calldata], {"from": deployer})
