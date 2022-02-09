"""
Conftest for integration tests
"""

import pytest
from brownie import Contract, interface

from data.access_control import APPROVED_COMMAND

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
def uni_router(request):
    router = request.param
    yield Contract.from_abi(
        f"{router['venue']} router", router["address"], interface.IUniswapV2Router02.abi
    )


@pytest.fixture(scope="module")
def venue_cswap(deployer, invoker, CSwap, uni_router, weth):
    contract = deployer.deploy(CSwap, weth.address, uni_router.address)
    invoker.grantRole(APPROVED_COMMAND, contract.address, {"from": deployer})
    yield contract


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_abi(
        "WETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", interface.IWETH.abi
    )


@pytest.fixture(scope="module")
def token(request):
    token = request.param
    yield Contract.from_abi(token["name"], token["address"], interface.IERC20.abi)
