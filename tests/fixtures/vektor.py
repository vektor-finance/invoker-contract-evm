import pytest
from brownie import ZERO_ADDRESS
from eth_abi import encode_single

from data.access_control import APPROVED_COMMAND
from data.anyswap import get_anyswap_tokens_for_chain
from data.chain import get_wnative_address


@pytest.fixture(scope="module")
def deployer_registry(registry_deployer_user, DeployerRegistry, deployer):
    yield registry_deployer_user.deploy(DeployerRegistry, deployer)


@pytest.fixture(scope="module")
def invoker(deployer_registry, deployer, Invoker):
    tx = deployer_registry.deployNewContract(
        Invoker.bytecode, "0x", 0, encode_single("address", deployer.address), {"from": deployer}
    )
    yield Invoker.at(tx.return_value)


@pytest.fixture(scope="module")
def cswap(invoker, deployer, CSwapUniswapV2):
    contract = deployer.deploy(CSwapUniswapV2)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cwrap(deployer_registry, invoker, deployer, CWrap, wnative):
    tx = deployer_registry.deployNewContract(
        CWrap.bytecode, "0x", 0, encode_single("address", wnative.address), {"from": deployer}
    )
    contract = CWrap.at(tx.return_value)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cmove(deployer, invoker, CMove):
    contract = deployer.deploy(CMove)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cbridge_anyswap(deployer, invoker, CBridgeAnyswap, connected_chain):
    wnative = get_wnative_address(connected_chain)
    anyswap_tokens = get_anyswap_tokens_for_chain(connected_chain)
    any_native_tokens = [
        token["anyAddress"] for token in anyswap_tokens if token["underlyingAddress"] == wnative
    ]
    try:
        any_native_token = any_native_tokens[0]
    except IndexError:
        any_native_token = ZERO_ADDRESS
    contract = deployer.deploy(CBridgeAnyswap, wnative, any_native_token)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract
