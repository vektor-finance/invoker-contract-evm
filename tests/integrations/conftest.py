"""
Conftest for integration tests
"""

import pytest
from brownie import Contract, interface

# Contracts from config file


@pytest.fixture(scope="module")
def uni_router(request):
    router = request.param
    yield Contract.from_abi(
        f"{router['venue']} router", router["address"], interface.IUniswapV2Router02.abi
    )


@pytest.fixture(scope="module")
def weth(request):
    yield Contract.from_abi("WETH", request.param["address"], interface.IWETH.abi)


@pytest.fixture(scope="module")
def token(request):
    token = request.param
    yield Contract.from_abi(token["name"], token["address"], interface.IERC20.abi)
