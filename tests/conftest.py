import pytest
from brownie import Contract


# User accounts
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture(scope="module")
def deployer(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


# Deploy vektor contracts
APPROVED_COMMAND = "410a6a8d01da3028e7c041b5925a6d26ed38599db21a26cf9a5e87c68941f98a"


@pytest.fixture(scope="module", autouse=True)
def invoker(deployer, Invoker, cmove, cswap):
    contract = deployer.deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})  # approve commands
    contract.grantRole(APPROVED_COMMAND, cswap.address, {"from": deployer})
    yield contract


@pytest.fixture(scope="module", autouse=True)
def cswap(deployer, CSwap, weth, uniswapfactory):
    yield deployer.deploy(CSwap, weth.address, uniswapfactory.address)


@pytest.fixture(scope="module", autouse=True)
def cmove(deployer, CMove):
    yield deployer.deploy(CMove)


# Mainnet ethereum contracts


@pytest.fixture(scope="module")
def uni_router():
    yield Contract.from_explorer("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


@pytest.fixture(scope="module")
def uni_dai_eth():
    yield Contract.from_explorer("0xa478c2975ab1ea89e8196811f51a7b7ade33eb11")


@pytest.fixture(scope="module")
def weth():
    yield Contract.from_explorer("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def dai():
    yield Contract.from_explorer("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def usdc():
    yield Contract.from_explorer("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")


@pytest.fixture(scope="module")
def link():
    yield Contract.from_explorer("0x514910771AF9Ca656af840dff83E8264EcF986CA")


@pytest.fixture(scope="module")
def world():  # deflationary token with burn on transfer
    yield Contract.from_explorer("0xBF494F02EE3FdE1F20BEE6242bCe2d1ED0c15e47")


@pytest.fixture(scope="module")
def uniswapfactory():
    yield Contract.from_explorer("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
