import pytest
from brownie import Contract

@pytest.fixture(scope="session")
def user(accounts):
    yield accounts[0]

@pytest.fixture
def uni_router():
    yield Contract.from_explorer('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')

@pytest.fixture(scope="session")
def uni_dai_eth():
    yield Contract.from_explorer("0xa478c2975ab1ea89e8196811f51a7b7ade33eb11")

@pytest.fixture(scope="session")
def WETH():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

@pytest.fixture(scope="session")
def dai():
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")

    