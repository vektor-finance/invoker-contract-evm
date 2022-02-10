import brownie
import pytest

from data.access_control import APPROVED_COMMAND, DEFAULT_ADMIN_ROLE, ROLE_PAUSER


def test_owner(invoker, deployer):
    assert invoker.hasRole(DEFAULT_ADMIN_ROLE, deployer)


@pytest.fixture
def invokerNoApproval(deployer, Invoker):
    yield deployer.deploy(Invoker)


def test_should_revert_if_command_not_approved(invokerNoApproval, cmove, alice, mock_erc20):
    mock_erc20.mint(alice, 100 * 1e18)
    calldata = cmove.moveERC20In.encode_input(mock_erc20, 100 * 1e18)
    with brownie.reverts("Command not approved"):
        invokerNoApproval.invoke([cmove.address], [calldata], {"from": alice})


def test_should_permit_approved_commands(invoker, cmove, alice, deployer, mock_erc20):
    mock_erc20.mint(alice, 100 * 1e18)
    invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})
    calldata = cmove.moveERC20In.encode_input(mock_erc20.address, 100 * 1e18)
    mock_erc20.approve(invoker.address, 100 * 1e18, {"from": alice})
    invoker.invoke([cmove.address], [calldata], {"from": alice})
    assert mock_erc20.balanceOf(invoker.address) == 100 * 1e18


def test_non_admin_users_cant_approve_commands(invoker, cmove, alice):
    with brownie.reverts():
        invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": alice})


# PAUSABLE FUNCTIONALITY BELOW


def test_deployer_is_initial_pauser(invoker, deployer):
    assert invoker.hasRole(ROLE_PAUSER, deployer)


def test_initially_deployed_unpaused(invoker):
    assert not invoker.paused()


def test_pause_from_admin(invoker, deployer):
    tx = invoker.pause({"from": deployer})
    assert invoker.paused()
    events = tx.events
    assert "Paused" in events


def test_unpause_from_admin(invoker, deployer):
    invoker.pause({"from": deployer})  # need to pause contract first
    tx = invoker.unpause({"from": deployer})
    assert not invoker.paused()
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


def test_add_pauser(invoker, deployer, alice):
    invoker.grantRole(ROLE_PAUSER, alice, {"from": deployer})
    invoker.pause({"from": alice})
    assert invoker.paused()


def test_remove_pauser(invoker, deployer, alice):
    invoker.grantRole(ROLE_PAUSER, alice, {"from": deployer})
    invoker.revokeRole(ROLE_PAUSER, alice, {"from": deployer})
    with brownie.reverts("PAC: Invalid role"):
        invoker.pause({"from": alice})
