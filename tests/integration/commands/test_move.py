import brownie


def test_move_erc20_in(alice, tokens_for_alice, invoker, cmove):
    amount = tokens_for_alice.balanceOf(alice)
    tokens_for_alice.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice.address, amount)
    invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})
    assert tokens_for_alice.balanceOf(invoker.address) == amount
    assert tokens_for_alice.balanceOf(alice) == 0


def test_move_erc20_out(alice, tokens_for_alice, invoker, cmove):
    amount = tokens_for_alice.balanceOf(alice)
    tokens_for_alice.transfer(invoker.address, amount, {"from": alice})
    calldata_move_out = cmove.moveERC20Out.encode_input(tokens_for_alice.address, alice, amount)
    invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})
    assert tokens_for_alice.balanceOf(invoker.address) == 0
    assert tokens_for_alice.balanceOf(alice) == amount


def test_move_all_erc20_out(alice, tokens_for_alice, invoker, cmove):
    amount = tokens_for_alice.balanceOf(alice)
    calldata_move_all_out = cmove.moveAllERC20Out.encode_input(tokens_for_alice.address, alice)
    invoker.invoke([cmove.address], [calldata_move_all_out], {"from": alice})
    assert tokens_for_alice.balanceOf(invoker.address) == 0
    assert tokens_for_alice.balanceOf(alice) == amount


def test_fail_insufficient_balance_move_erc20_in(alice, tokens_for_alice, invoker, cmove, bob):
    amount = tokens_for_alice.balanceOf(alice)
    tokens_for_alice.transfer(bob.address, amount, {"from": alice})
    tokens_for_alice.approve(invoker.address, amount, {"from": alice})
    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


def test_fail_insufficient_allowance_move_erc20_in(alice, tokens_for_alice, invoker, cmove):
    amount = tokens_for_alice.balanceOf(alice)
    calldata_move_in = cmove.moveERC20In.encode_input(tokens_for_alice.address, amount)
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_in], {"from": alice})


def test_fail_insufficient_balance_move_erc20_out(alice, tokens_for_alice, invoker, cmove, bob):
    amount = tokens_for_alice.balanceOf(alice)
    calldata_move_out = cmove.moveERC20In.encode_input(tokens_for_alice.address, amount)
    tokens_for_alice.transfer(bob.address, amount, {"from": alice})
    with brownie.reverts():
        invoker.invoke([cmove.address], [calldata_move_out], {"from": alice})
