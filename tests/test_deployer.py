import brownie
import pytest
from brownie import web3
from brownie.test import given, strategy

ZERO_BYTES = "0x0000000000000000000000000000000000000000000000000000000000000000"

"""
Invoker <Contract>
   └─ constructor -  avg: 1204890  avg (confirmed): 1204890  low: 1204890  high: 1204890
MasterDeployer <Contract>
   ├─ deployCode  -  avg: 1173278  avg (confirmed): 1261974  low:  108935  high: 1262076
   └─ constructor -  avg:  415886  avg (confirmed):  415886  low:  415886  high:  415886
"""


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
    create3_invoker = master_deployer.deployCode(
        Invoker.bytecode,
        ZERO_BYTES,
        {"from": deployer},
    ).return_value
    normal_invoker = deployer.deploy(Invoker)
    assert web3.eth.get_code(create3_invoker) == web3.eth.get_code(normal_invoker.address)


def test_ownership(master_deployer, deployer, alice, Invoker):
    with brownie.reverts():
        master_deployer.deployCode(Invoker.bytecode, ZERO_BYTES, {"from": alice})
    master_deployer.deployCode(Invoker.bytecode, ZERO_BYTES, {"from": deployer})
