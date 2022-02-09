"""
conftest for fixtures that are present during ALL tests (core + integrations)
Most fixtures will be generated in subfolders
"""
from pathlib import Path

import pytest
from brownie._config import CONFIG
from brownie.project.main import get_loaded_projects

from data.chain import get_chain_from_network_name


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


# Integrations

_network = ""
_chain = {}


def pytest_sessionstart():
    global _chain, _network
    _network = CONFIG.settings["networks"]["default"]
    if CONFIG.argv["network"]:
        _network = CONFIG.argv["network"]
    (_chain, _) = get_chain_from_network_name(_network)


def pytest_ignore_collect(path):
    project = get_loaded_projects()[0]
    path = Path(path).relative_to(project._path)

    path_parts = path.parts[1:-1]

    if path.is_dir():
        return None

    # ignore integration tests if on 'hardhat' network (dev)
    if path_parts[:1] == ("integrations",):
        return _network == "hardhat"


def pytest_generate_tests(metafunc):

    if "token" in metafunc.fixturenames:
        if _chain["id"] != "dev":
            tokens = [asset for asset in _chain["assets"] if asset.get("address")]
            token_names = [token["name"] for token in tokens]
            metafunc.parametrize("token", tokens, ids=token_names, indirect=True)
