import pytest


@pytest.fixture(scope="module")
def deployer(accounts):
    yield accounts[-1]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[4]
