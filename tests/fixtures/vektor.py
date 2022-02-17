import pytest

from data.access_control import APPROVED_COMMAND


@pytest.fixture(scope="module")
def invoker(deployer, Invoker):
    yield deployer.deploy(Invoker)


@pytest.fixture(scope="module")
def cswap(invoker, deployer, CSwap, wnative, uni_router):
    contract = deployer.deploy(CSwap, wnative.address, uni_router.address)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cmove(deployer, invoker, CMove):
    contract = deployer.deploy(CMove)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cbridge(deployer, invoker, CBridge, any_native_token, wnative):
    contract = deployer.deploy(CBridge, wnative, any_native_token["address"])
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract
