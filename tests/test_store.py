import brownie
import pytest


@pytest.fixture
def store(deployer, Store):
    yield deployer.deploy(Store)


def print_val(addr, key):
    a = brownie.web3.eth.get_storage_at(addr, key)
    print(addr, key.hex(), a.hex())


def test_store(store):
    acct = store.address
    var_location = "{0:#0{1}x}".format(0, 66)
    index_location = "{0:#0{1}x}".format(1, 66)
    print(index_location, var_location)
    key = brownie.web3.keccak(hexstr=(index_location + var_location[2:]))
    print_val(acct, key)


# 0x0000000000000000000000000000000000000000000000000000000000000003
