import brownie


def test_owner(invoker, deployer):
    assert invoker.hasRole("0x00", deployer)


def test_should_revert_if_unequal_length(invoker, mock_erc20, alice, bob):
    calldata_one = mock_erc20.transferFrom.encode_input(alice, bob, 1000)
    calldata_two = mock_erc20.transferFrom.encode_input(alice, bob, 1000)
    with brownie.reverts("dev: to+data length not equal"):
        invoker.invoke([mock_erc20.address], [calldata_one, calldata_two], {"from": alice})


def test_cannot_invoke_when_contract_paused(invoker, alice, deployer, cmove, mock_erc20):
    invoker.pause({"from": deployer})
    mock_erc20.mint(alice, 100 * 1e18, {"from": alice})
    mock_erc20.approve(invoker.address, 100 * 1e18, {"from": alice})
    calldata = cmove.moveERC20In.encode_input(mock_erc20, 100 * 1e18)
    with brownie.reverts("PAC: Paused"):
        invoker.invoke([cmove.address], [calldata], {"from": deployer})
