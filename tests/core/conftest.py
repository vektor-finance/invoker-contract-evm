import pytest


# TEST TOKENS
@pytest.fixture(scope="module")
def mock_erc20(deployer, MockERC20):
    yield deployer.deploy(MockERC20, "Test Token", "TST", 18)


@pytest.fixture(scope="module")
def mock_deflationary_erc20(deployer, MockERC20Deflationary):
    yield deployer.deploy(MockERC20Deflationary, "Deflationary Test Token", "DTT", 18)


@pytest.fixture(scope="module")
def mock_rebasing_erc20(deployer, MockERC20Rebasing):
    yield deployer.deploy(MockERC20Rebasing, "Rebasing Test Token", "RTT", 18)


@pytest.fixture(scope="module")
def mock_erc721(deployer, MockERC721):
    yield deployer.deploy(MockERC721, "Mock ERC721", "NFT TEST")
