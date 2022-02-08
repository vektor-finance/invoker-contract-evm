import brownie

# ETH tests


"""
@given(value=strategy("uint256", max_value="1000 ether"), to=strategy("address"))
def test_move_eth_to_single_address(alice, to, invoker, cmove, value):
    alice_starting_balance = alice.balance()
    to_starting_balance = to.balance()
    calldata_transfer_one_eth = cmove.moveEth.encode_input(to.address, value)
    invoker.invoke([cmove.address], [calldata_transfer_one_eth], {"from": alice, "value": value})
    if alice is not to:
        assert alice.balance() == alice_starting_balance - value
        assert to.balance() == to_starting_balance + value


@given(
    value1=strategy("uint256", max_value="500 ether"),
    user1=strategy("address"),
    value2=strategy("uint256", max_value="500 ether"),
    user2=strategy("address"),
)
def test_move_eth_to_multiple_addresses(alice, user1, user2, value1, value2, invoker, cmove):
    amount = 100 * 1e18
    alice_starting_balance = alice.balance()
    user1_starting_balance = user1.balance()
    user2_starting_balance = user2.balance()
    calldata_transfer_eth_to_user1 = cmove.moveEth.encode_input(user1.address, value1)
    calldata_transfer_eth_to_user2 = cmove.moveEth.encode_input(user2.address, value2)
    invoker.invoke(
        [cmove.address, cmove.address],
        [calldata_transfer_eth_to_user1, calldata_transfer_eth_to_user2],
        {"from": alice, "value": value1 + value2},
    )
    if alice in [user1, user2]:
        pass
    else:
        assert alice.balance() == alice_starting_balance - value1 - value2
        if user1 is not user2:
            assert user1.balance() == user1_starting_balance + value1
            assert user2.balance() == user2_starting_balance + value2


@given(value=strategy("uint256", max_value="1000 ether"), to=strategy("address"))
def test_move_all_eth_out_to_single_address(alice, to, invoker, cmove, value):
    alice_starting_balance = alice.balance()
    to_starting_balance = to.balance()
    calldata_transfer_all_eth = cmove.moveAllEthOut.encode_input(to.address)
    invoker.invoke([cmove.address], [calldata_transfer_all_eth], {"from": alice, "value": value})
    assert invoker.balance() == 0
    if alice is not to:
        assert alice.balance() == alice_starting_balance - value
        assert to.balance() == to_starting_balance + value


@given(
    value=strategy("uint256", max_value="1000 ether"),
    user=strategy("address"),
)
def test_move_all_erc20_out(alice, value, user, dai, weth, uni_router, cmove, invoker):
    get_dai_for_user(dai, alice, weth, uni_router)
    alice_starting_balance = dai.balanceOf(alice.address)
    receiver_starting_balance = dai.balanceOf(user.address)

    calldata_transfer_dai_to_invoker = cmove.moveERC20In.encode_input(dai.address, value)
    calldata_transfer_all_dai_to_receiver = cmove.moveAllERC20Out.encode_input(
        dai.address, user.address
    )
    dai.approve(invoker.address, value, {"from": alice})
    invoker.invoke(
        [cmove.address, cmove.address],
        [calldata_transfer_dai_to_invoker, calldata_transfer_all_dai_to_receiver],
        {"from": alice},
    )
    assert dai.balanceOf(invoker.address) == 0
    if user == alice:  # if user is alice then these tests will incorrectly fail
        pass
    else:
        assert dai.balanceOf(alice.address) == alice_starting_balance - value
        assert dai.balanceOf(user.address) == receiver_starting_balance + value
"""


# ERC20 TESTS


def test_move_erc20_in(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_erc20.mint(alice, amount, {"from": alice})
    mock_erc20.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(mock_erc20.address, amount)
    invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})
    assert mock_erc20.balanceOf(invoker.address) == amount
    assert mock_erc20.balanceOf(alice) == 0


def test_move_erc20_out(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_erc20.mint(invoker.address, amount, {"from": alice})
    calldata_move_out = cmove.moveERC20Out.encode_input(mock_erc20.address, alice, amount)
    invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})
    assert mock_erc20.balanceOf(invoker.address) == 0
    assert mock_erc20.balanceOf(alice) == amount


def test_move_all_erc20_out(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_erc20.mint(invoker.address, amount, {"from": alice})
    calldata_move_all_out = cmove.moveAllERC20Out.encode_input(mock_erc20.address, alice)
    invoker.invoke([cmove.address], [calldata_move_all_out], {"from": alice})
    assert mock_erc20.balanceOf(invoker.address) == 0
    assert mock_erc20.balanceOf(alice) == amount


def test_fail_insufficient_balance_move_erc20_in(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_erc20.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(mock_erc20.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


def test_fail_insufficient_allowance_move_erc20_in(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_erc20.mint(alice, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(mock_erc20.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


def test_fail_insufficient_balance_move_erc20_out(alice, mock_erc20, invoker, cmove):
    amount = 100 * 1e18
    calldata_move_out = cmove.moveERC20In.encode_input(mock_erc20.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})


# Deflationary Tokens


def test_move_deflationary_erc20_in(alice, mock_deflationary_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_deflationary_erc20.mint(alice, amount, {"from": alice})
    mock_deflationary_erc20.approve(invoker.address, amount, {"from": alice})
    calldata_move_deflationary_in = cmove.moveERC20In.encode_input(
        mock_deflationary_erc20.address, amount
    )
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_move_deflationary_in], {"from": alice})


def test_move_deflationary_erc20_out(alice, mock_deflationary_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_deflationary_erc20.mint(invoker.address, amount, {"from": alice})
    calldata_move_deflationary_out = cmove.moveERC20Out.encode_input(
        mock_deflationary_erc20.address, alice, amount
    )
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_move_deflationary_out], {"from": alice})


def test_move_all_deflationary_erc20_out(alice, mock_deflationary_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_deflationary_erc20.mint(invoker.address, amount, {"from": alice})
    calldata_move_all_deflationary_out = cmove.moveAllERC20Out.encode_input(
        mock_deflationary_erc20.address, alice
    )
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_move_all_deflationary_out], {"from": alice})
