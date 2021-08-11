import pytest
from brownie.convert import to_bytes
from brownie.test import given, strategy

KECCAK_MSGSENDER = "0xb2f2618cecbbb6e7468cc0f2aa43858ad8d153e0280b22285e28e853bb9d453a"
KECCAK_BALANCE = "0xea06f38f7e4f15e87567361213c28f235cccdaa1d7fd34c9db1dfe9489c6a091"
KECCAK_BYTES = "0xb963e9b45d014edd60cff22ec9ad383335bbc3f827be2aee8e291972b0fadcf2"
KECCAK_BOOL = "0xc1053bdab4a5cf55238b667c39826bbb11a58be126010e7db397c1b67c24271b"
NULL_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def storage(deployer, Storage):
    return deployer.deploy(Storage)


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


def test_null(storage):
    assert storage.read("") == "0x"


@given(address=strategy("address"))
def test_set_sender(storage, address, deployer):
    storage.writeAddress(KECCAK_MSGSENDER, address, {"from": deployer})
    assert storage.readAddress(KECCAK_MSGSENDER) == address


def test_ensure_reset(storage):
    assert storage.readAddress(KECCAK_MSGSENDER) == NULL_ADDRESS


@given(value=strategy("uint256"))
def test_set_value(storage, value, deployer):
    storage.writeUint256(KECCAK_BALANCE, value, {"from": deployer})
    assert storage.readUint256(KECCAK_BALANCE) == value


@given(test_bytes=strategy("bytes32"))
def test_set_bytes(storage, test_bytes, deployer):
    storage.write(KECCAK_BYTES, test_bytes, {"from": deployer})
    assert to_bytes(storage.read(KECCAK_BYTES)) == test_bytes


def test_set_true_then_false(storage, deployer):
    storage.writeBool(KECCAK_BOOL, True, {"from": deployer})
    assert storage.readBool(KECCAK_BOOL)

    storage.writeBool(KECCAK_BOOL, False, {"from": deployer})
    assert not storage.readBool(KECCAK_BOOL)
