import pytest
from brownie import web3
from brownie.test import given, strategy


@pytest.fixture(scope="module")
def master_deployer(deployer, MasterDeployer):
    yield deployer.deploy(MasterDeployer)


@given(salt=strategy("bytes32"))
def test_salt(Invoker, master_deployer, deployer, salt):
    expected_address = master_deployer.addressOf(salt)
    tx = master_deployer.deployCode(
        Invoker.bytecode,
        salt,
        {"from": deployer},
    )
    event = tx.events["ContractDeployed"]
    assert event["deployedAddress"] == expected_address


def test_bytecode(Invoker, master_deployer, deployer):
    salt = "0x0000000000000000000000000000000000000000000000000000000000000000"
    create3_invoker = master_deployer.deployCode(
        Invoker.bytecode,
        salt,
        {"from": deployer},
    ).return_value
    normal_invoker = deployer.deploy(Invoker)
    assert web3.eth.get_code(create3_invoker) == web3.eth.get_code(normal_invoker.address)
