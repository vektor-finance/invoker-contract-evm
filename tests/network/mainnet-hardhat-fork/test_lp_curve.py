import pytest

from data.access_control import APPROVED_COMMAND


@pytest.fixture(scope="module")
def clp_curve(invoker, deployer, CLPCurve):
    contract = deployer.deploy(CLPCurve)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


def test_deposit(invoker, cmove, alice, clp_curve):
    pass
