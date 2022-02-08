"""
Conftest for integration tests
"""

import pytest
from brownie import Contract, interface
from brownie._config import CONFIG

from data.chain import get_chain_from_network_name

# Deploy vektor contracts
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"

# Mainnet uniswap router
UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


@pytest.fixture(scope="module", autouse=True)
def invoker(deployer, Invoker, cmove, cswap):
    contract = deployer.deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})  # approve commands
    contract.grantRole(APPROVED_COMMAND, cswap.address, {"from": deployer})
    yield contract


@pytest.fixture(scope="module", autouse=True)
def cswap(deployer, CSwap, weth):
    yield deployer.deploy(CSwap, weth.address, UNISWAP_ROUTER)


@pytest.fixture(scope="module", autouse=True)
def cmove(deployer, CMove):
    yield deployer.deploy(CMove)


# Mainnet ethereum contracts


@pytest.fixture(scope="module")
def uni_router():
    yield Contract.from_explorer("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


@pytest.fixture(scope="module")
def weth():
    WETH = interface.IWETH
    yield Contract.from_abi("WETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", WETH.abi)


@pytest.fixture(scope="module")
def dai():
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def usdc():
    yield Contract.from_explorer("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")


_network = ""
_chain = {}


def pytest_sessionstart():
    global _network, _chain
    _network = CONFIG.argv["network"]
    (_chain, _) = get_chain_from_network_name(_network)


def pytest_ignore_collect():
    # ignore integration tests if on 'hardhat' network (dev)
    if _network == "hardhat":
        return True


def pytest_generate_tests(metafunc):
    tokens = [asset for asset in _chain["assets"] if asset.get("address")]
    token_addresses = [token["address"] for token in tokens]
    token_names = [token["name"] for token in tokens]
    if "token" in metafunc.fixturenames:
        metafunc.parametrize("token", token_addresses, ids=token_names)
