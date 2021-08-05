import pytest

from brownie import Invoker, accounts

@pytest.fixture(scope="module")
def invoker():
    return accounts[0].deploy(Invoker)

def test_owner(invoker):
    assert invoker.owner() == accounts[0]