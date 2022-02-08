import pytest

from data.access_control import APPROVED_COMMAND


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


@pytest.fixture(scope="module", autouse=True)
def invoker(deployer, Invoker, cmove):
    contract = deployer.deploy(Invoker)
    contract.grantRole(APPROVED_COMMAND, cmove.address, {"from": deployer})  # approve commands
    yield contract


@pytest.fixture(scope="module", autouse=True)
def cmove(deployer, CMove):
    yield deployer.deploy(CMove)


# TEST TOKENS
@pytest.fixture(scope="module")
def mock_erc20(deployer, MockERC20):
    yield deployer.deploy(MockERC20, "Test Token", "TST", 18)


@pytest.fixture(scope="module")
def mock_deflationary_erc20(deployer, MockERC20Deflationary):
    yield deployer.deploy(MockERC20Deflationary, "Deflationary Test Token", "DTT", 18)
