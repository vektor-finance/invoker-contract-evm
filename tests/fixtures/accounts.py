import pytest


@pytest.fixture(scope="module")
def deployer(accounts):
    yield accounts[-1]


@pytest.fixture(scope="module")
def registry_deployer_user(accounts):
    yield accounts[-2]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]
