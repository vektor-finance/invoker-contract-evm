import time

import brownie
import pytest
from brownie import CMove, Invoker, accounts

# Roles
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"
# keccak256("APPROVED_COMMAND_IMPLEMENTATION")


@pytest.fixture(scope="module")
def invoker():
    return accounts[0].deploy(Invoker)


@pytest.fixture(scope="module")
def cmove():
    return accounts[0].deploy(CMove)


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_owner(invoker):
    assert invoker.hasRole("0x00", accounts[0]) is True


def get_dai_for_user(dai, user, WETH, uni_router):
    path = [WETH.address, dai.address]
    uni_router.swapExactETHForTokens(
        2700 * 1e18, path, user, int(time.time()) + 1, {"from": user, "value": 1e18}
    )
    assert dai.balanceOf(user) > 1 * 1e18


def test_should_revert_if_command_not_approved(invoker, cmove, dai, user, WETH, uni_router):
    get_dai_for_user(dai, user, WETH, uni_router)
    calldata = cmove.move.encode_input(dai.address, user.address, invoker.address, 100 * 1e18)
    with brownie.reverts("Command not approved"):
        invoker.invoke([cmove.address], [calldata], {"from": accounts[0]})


def test_should_permit_approved_commands(invoker, cmove, dai, user, WETH, uni_router):
    get_dai_for_user(dai, user, WETH, uni_router)
    invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": accounts[0]})
    calldata = cmove.move.encode_input(dai.address, user.address, invoker.address, 100 * 1e18)
    dai.approve(invoker.address, 100 * 1e18, {"from": user})
    assert dai.allowance(user, invoker.address) == 100 * 1e18
    invoker.invoke([cmove.address], [calldata], {"from": accounts[0]})
    assert dai.balanceOf(invoker.address) == 100 * 1e18


def test_non_admin_users_cant_approve_commands(invoker, cmove):
    with brownie.reverts():
        invoker.grantRole(APPROVED_COMMAND, cmove.address, {"from": accounts[1]})
