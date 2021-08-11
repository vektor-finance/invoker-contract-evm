import brownie
import pytest
from helpers import APPROVED_COMMAND, get_dai_for_user


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_owner(invoker, deployer):
    assert invoker.hasRole("0x00", deployer)


@pytest.fixture
def invokerNoApproval(deployer, Invoker):
    yield deployer.deploy(Invoker)


def test_should_revert_if_command_not_approved(
    invokerNoApproval, cmove, dai, deployer, weth, uni_router
):
    invoker = invokerNoApproval
    get_dai_for_user(dai, deployer, weth, uni_router)
    calldata = cmove.move.encode_input(dai.address, invoker.address, 100 * 1e18)
    with brownie.reverts("Command not approved"):
        invoker.invoke([cmove.address], [calldata], {"from": deployer})


def test_should_permit_approved_commands(invoker, cmove, dai, weth, uni_router, deployer):
    get_dai_for_user(dai, deployer, weth, uni_router)
    invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})
    calldata = cmove.move.encode_input(dai.address, invoker.address, 100 * 1e18)
    dai.approve(invoker.address, 100 * 1e18, {"from": deployer})
    assert dai.allowance(deployer, invoker.address) == 100 * 1e18
    invoker.invoke([cmove.address], [calldata], {"from": deployer})
    assert dai.balanceOf(invoker.address) == 100 * 1e18


def test_non_admin_users_cant_approve_commands(invoker, cmove, alice):
    with brownie.reverts():
        invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": alice})
