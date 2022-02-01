import brownie
import pytest

from tests.helpers import APPROVED_COMMAND, DEFAULT_ADMIN_ROLE, PAUSER, get_dai_for_user


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_owner(invoker, deployer):
    assert invoker.hasRole(DEFAULT_ADMIN_ROLE, deployer)


@pytest.fixture
def invokerNoApproval(deployer, Invoker):
    yield deployer.deploy(Invoker)


def test_should_revert_if_command_not_approved(
    invokerNoApproval, cmove, dai, deployer, weth, uni_router
):
    invoker = invokerNoApproval
    get_dai_for_user(dai, deployer, weth, uni_router)
    calldata = cmove.moveERC20In.encode_input(dai.address, 100 * 1e18)
    with brownie.reverts("Command not approved"):
        invoker.invoke([cmove.address], [calldata], {"from": deployer})


def test_should_permit_approved_commands(invoker, cmove, dai, weth, uni_router, deployer):
    get_dai_for_user(dai, deployer, weth, uni_router)
    invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})
    calldata = cmove.moveERC20In.encode_input(dai.address, 100 * 1e18)
    dai.approve(invoker.address, 100 * 1e18, {"from": deployer})
    assert dai.allowance(deployer, invoker.address) == 100 * 1e18
    invoker.invoke([cmove.address], [calldata], {"from": deployer})
    assert dai.balanceOf(invoker.address) == 100 * 1e18


def test_non_admin_users_cant_approve_commands(invoker, cmove, alice):
    with brownie.reverts():
        invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": alice})


# PAUSABLE FUNCTIONALITY BELOW


def test_deployer_is_initial_pauser(invoker, deployer):
    assert invoker.hasRole(PAUSER, deployer)


def test_initially_deployed_unpaused(invoker):
    assert invoker.paused() is False


def test_pause_from_admin(invoker, deployer):
    tx = invoker.pause({"from": deployer})
    assert invoker.paused() is True
    events = tx.events
    assert "Paused" in events


def test_unpause_from_admin(invoker, deployer):
    invoker.pause({"from": deployer})  # need to pause contract first
    tx = invoker.unpause({"from": deployer})
    assert invoker.paused() is False
    events = tx.events
    assert "Unpaused" in events


def test_cannot_pause_if_paused(invoker, deployer):
    invoker.pause({"from": deployer})
    with brownie.reverts("PAC: Paused"):
        invoker.pause({"from": deployer})


def test_cannot_unpause_if_unpaused(invoker, deployer):
    with brownie.reverts("PAC: Not paused"):
        invoker.unpause({"from": deployer})


def test_only_approved_can_pause(invoker, alice):
    with brownie.reverts("PAC: Invalid role"):
        invoker.pause({"from": alice})


def test_only_approved_can_unpause(invoker, deployer, alice):
    invoker.pause({"from": deployer})
    with brownie.reverts("PAC: Invalid role"):
        invoker.unpause({"from": alice})
