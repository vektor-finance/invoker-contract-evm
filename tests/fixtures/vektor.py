import pytest
from brownie import ZERO_ADDRESS
from eth_abi import encode_single

from data.access_control import APPROVED_COMMAND
from data.chain import get_wnative_address


@pytest.fixture(scope="module")
def create2_deployer(registry_deployer_user, Create2Deployer, deployer):
    yield registry_deployer_user.deploy(Create2Deployer, deployer)


@pytest.fixture(scope="module")
def invoker(create2_deployer, deployer, Invoker):
    tx = create2_deployer.deployNewContract(
        Invoker.bytecode, "0x", 0, encode_single("address", deployer.address), {"from": deployer}
    )
    yield Invoker.at(tx.return_value)


@pytest.fixture(scope="module")
def cswap(invoker, deployer, CSwapUniswapV2):
    contract = deployer.deploy(CSwapUniswapV2)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})  # approve command
    yield contract


@pytest.fixture(scope="module")
def cwrap(create2_deployer, invoker, deployer, CWrap, wnative):
    tx = create2_deployer.deployNewContract(
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
def clend_aave(deployer, invoker, CLendAave):
    contract = deployer.deploy(CLendAave)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract


@pytest.fixture(scope="module")
def clend_compound(deployer, invoker, CLendCompoundV3):
    contract = deployer.deploy(CLendCompoundV3)
    invoker.grantRole(APPROVED_COMMAND, contract, {"from": deployer})
    yield contract
