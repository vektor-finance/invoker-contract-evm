import pytest

from data.access_control import APPROVED_COMMAND
from data.anyswap import get_anyswap_tokens_for_chain
from data.chain import get_wnative_address


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
def cbridge(deployer, invoker, CBridge, connected_chain):
    wnative = get_wnative_address(connected_chain)
    anyswap_tokens = get_anyswap_tokens_for_chain(connected_chain)
    any_native_tokens = [
        token["anyAddress"] for token in anyswap_tokens if token["underlyingAddress"] == wnative
    ]
    try:
        any_native_token = any_native_tokens[0]
    except IndexError:
        pytest.skip("No native anyToken")
    contract = deployer.deploy(CBridge, wnative, any_native_token)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract
