import pytest
from brownie import Contract

# User accounts


@pytest.fixture(scope="module")
def deployer(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    return accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    return accounts[2]


# Deploy vektor contracts
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


@pytest.fixture
def invoker(deployer, Invoker, cmove, cswap):
    contract = deployer.deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})  # approve commands
    contract.grantRole(APPROVED_COMMAND, cswap.address, {"from": deployer})
    yield contract


@pytest.fixture
def cswap(deployer, CSwap):
    yield deployer.deploy(CSwap)


@pytest.fixture
def cmove(deployer, CMove):
    yield deployer.deploy(CMove)


# Mainnet ethereum contracts


@pytest.fixture
def uni_router():
    yield Contract.from_explorer("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


@pytest.fixture
def uni_dai_eth():
    yield Contract.from_explorer("0xa478c2975ab1ea89e8196811f51a7b7ade33eb11")


@pytest.fixture
def weth():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture
def dai():
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture
def usdc():
    yield Contract.from_explorer("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")


@pytest.fixture
def link():
    yield Contract.from_explorer("0x514910771AF9Ca656af840dff83E8264EcF986CA")
