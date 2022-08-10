import brownie
import pytest
import solcx
from brownie import Contract
from eth_abi import encode
from eth_utils import keccak

from helpers.addresses import get_create2_address


def get_salt_bytes(salt: int):
    return "0x" + (salt).to_bytes(32, "big").hex()


def predict_deployment_address(bytecode, deployer):
    b_creation_code = bytes.fromhex(bytecode)
    init_code_hash = "0x" + keccak(b_creation_code).hex()
    predicted_address = get_create2_address(deployer.address, get_salt_bytes(0), init_code_hash)
    return predicted_address


def test_deployment_no_args(create2_deployer, deployer):
    compiled = solcx.compile_source(
        """
pragma solidity >= 0.8.0;
contract Test {
    uint256 public foo = 0;
    constructor() {
        foo = 5;
    }
    function bar() external view returns (uint256) {
        return foo;
    }
}""",
        solc_version="0.8.9",
    )["<stdin>:Test"]
    init_bytecode = compiled["bin"]

    contract_address = create2_deployer.deployNewContract(
        init_bytecode, get_salt_bytes(0), 0, b"", {"from": deployer}
    ).return_value

    assert contract_address == predict_deployment_address(init_bytecode, create2_deployer)
    assert Contract.from_abi("test", contract_address, compiled["abi"]).bar() == 5


def test_deployment_with_args(create2_deployer, deployer):
    compiled = solcx.compile_source(
        """
pragma solidity >= 0.8.0;
interface Deployer {
    function deployArgs() external view returns (bytes memory);
}
contract Test {
    uint256 public foo = 0;
    constructor() {
        foo = abi.decode(Deployer(msg.sender).deployArgs(),(uint256));
    }
    function bar() external view returns (uint256) {
        return foo;
    }
}""",
        solc_version="0.8.9",
    )["<stdin>:Test"]
    init_bytecode = compiled["bin"]

    contract_address = create2_deployer.deployNewContract(
        init_bytecode, get_salt_bytes(0), 0, encode(["uint256"], [3]), {"from": deployer}
    ).return_value

    assert contract_address == predict_deployment_address(init_bytecode, create2_deployer)
    assert Contract.from_abi("test", contract_address, compiled["abi"]).bar() == 3


@pytest.fixture(scope="module")
def dummy_contract():
    return solcx.compile_source(
        """
pragma solidity >= 0.8.0;
contract Test{
}
        """,
        solc_version="0.8.9",
    )["<stdin>:Test"]


def test_default_deployer_authorised(create2_deployer, deployer, dummy_contract):
    init_bytecode = dummy_contract["bin"]
    create2_deployer.deployNewContract(init_bytecode, get_salt_bytes(0), 0, b"", {"from": deployer})


def test_needs_authorisation(create2_deployer, alice, dummy_contract):
    init_bytecode = dummy_contract["bin"]
    with brownie.reverts("NOT_AUTHORISED"):
        create2_deployer.deployNewContract(
            init_bytecode, get_salt_bytes(0), 0, b"", {"from": alice}
        )


def test_approve_user(create2_deployer, deployer, alice, dummy_contract):
    create2_deployer.authoriseUser(alice, {"from": deployer})
    init_bytecode = dummy_contract["bin"]
    create2_deployer.deployNewContract(init_bytecode, get_salt_bytes(0), 0, b"", {"from": alice})


def test_revoke_user(create2_deployer, deployer, dummy_contract):
    create2_deployer.revokeUser(deployer, {"from": deployer})
    init_bytecode = dummy_contract["bin"]
    with brownie.reverts("NOT_AUTHORISED"):
        create2_deployer.deployNewContract(
            init_bytecode, get_salt_bytes(0), 0, b"", {"from": deployer}
        )


def test_bad_user_cant_approve(create2_deployer, alice):
    with brownie.reverts("NOT_AUTHORISED"):
        create2_deployer.authoriseUser(alice, {"from": alice})


def test_bad_user_cant_revoke(create2_deployer, deployer, alice):
    with brownie.reverts("NOT_AUTHORISED"):
        create2_deployer.revokeUser(deployer, {"from": alice})
