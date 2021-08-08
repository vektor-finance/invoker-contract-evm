import pytest

from brownie import Storage, accounts

#msg.sender = 0xb2f2618cecbbb6e7468cc0f2aa43858ad8d153e0280b22285e28e853bb9d453a

@pytest.fixture(scope="module")
def storage():
    return accounts[0].deploy(Storage)
    

def test_null(storage):
    assert storage.read('') == '0x'

def test_set_sender(storage):
    storage.write('0xb2f2618cecbbb6e7468cc0f2aa43858ad8d153e0280b22285e28e853bb9d453a',accounts[0].address)
    assert storage.read('0xb2f2618cecbbb6e7468cc0f2aa43858ad8d153e0280b22285e28e853bb9d453a') == accounts[0].address