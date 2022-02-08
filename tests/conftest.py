"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""

import pytest


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
