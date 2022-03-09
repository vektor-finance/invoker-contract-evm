from brownie.test import given, strategy


@given(value=strategy("uint256", max_value="1000 ether"))
def test_wrap_native(alice, invoker, wnative, cwrap, value):
    starting_balance = alice.balance()
    calldata_wrap = cwrap.wrapNative.encode_input(value)
    invoker.invoke([cwrap.address], [calldata_wrap], {"from": alice, "value": value})
    assert alice.balance() == starting_balance - value
    assert wnative.balanceOf(invoker) == value


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_native(alice, invoker, wnative, cwrap, value, bob):
    # bob mints wrapped native and sends to invoker
    start_balance = invoker.balance()
    wnative.deposit({"from": bob, "value": value})
    wnative.transfer(invoker, value, {"from": bob})
    calldata_unwrap = cwrap.unwrapWrappedNative.encode_input(value)
    invoker.invoke([cwrap.address], [calldata_unwrap], {"from": alice})
    assert invoker.balance() == value + start_balance
    assert wnative.balanceOf(invoker) == 0


@given(value=strategy("uint256", max_value="1000 ether"))
def test_unwrap_all_native(alice, invoker, wnative, cwrap, value, bob):
    # bob mints wrapped native and sends to invoker
    start_balance = invoker.balance()
    wnative.deposit({"from": bob, "value": value})
    wnative.transfer(invoker, value, {"from": bob})

    calldata_unwrap_all = cwrap.unwrapAllWrappedNative.encode_input()
    invoker.invoke([cwrap.address], [calldata_unwrap_all], {"from": alice})
    assert invoker.balance() == value + start_balance
    assert wnative.balanceOf(invoker) == 0
