import brownie
import pytest
from brownie.test import strategy

# ETH tests


class NativeEthStateMachine:
    value = strategy("uint256")
    from_address = strategy("address")
    to_address = strategy("address")
    multiple_recv = strategy("(address,uint256)[]")

    def __init__(cls, accounts, invoker, cmove):
        cls.accounts = accounts
        cls.invoker = invoker
        cls.cmove = cmove

    def setup(self):
        self.balances = {i: i.balance() for i in self.accounts}

    def rule_move_to_single(self, from_address, to_address, value):
        calldata_transfer_eth = self.cmove.moveNative.encode_input(to_address, value)
        if value <= self.balances[from_address]:
            self.invoker.invoke(
                [self.cmove.address],
                [calldata_transfer_eth],
                {"from": from_address, "value": value},
            )
            self.balances[from_address] -= value
            self.balances[to_address] += value
        else:
            pass

    def rule_move_to_multiple(self, from_address, multiple_recv):
        cmoves = [self.cmove.address] * len(multiple_recv)
        calldatas = [self.cmove.moveNative.encode_input(i[0].address, i[1]) for i in multiple_recv]
        total_value = sum(i[1] for i in multiple_recv)
        if total_value <= self.balances[from_address]:
            self.invoker.invoke(cmoves, calldatas, {"from": from_address, "value": total_value})
            self.balances[from_address] -= total_value
            for recv in multiple_recv:
                self.balances[recv[0]] += recv[1]
        else:
            pass

    def rule_move_sweep(self, from_address, to_address, value):
        calldata_sweep_eth = self.cmove.moveAllNativeOut.encode_input(to_address)
        if value <= self.balances[from_address]:
            self.invoker.invoke(
                [self.cmove.address],
                [calldata_sweep_eth],
                {"from": from_address, "value": value},
            )
            self.balances[from_address] -= value
            self.balances[to_address] += value
        else:
            pass

    def invariant(self):
        for address, amount in self.balances.items():
            assert address.balance() == amount
        assert self.invoker.balance() == 0


def test_stateful(accounts, state_machine, invoker, cmove):
    state_machine(NativeEthStateMachine, accounts, invoker, cmove)


def test_sweep_native_when_zero_balance(alice, invoker, cmove):
    start_balance = alice.balance()
    calldata_sweep = cmove.moveAllNativeOut.encode_input(alice.address)
    invoker.invoke([cmove.address], [calldata_sweep], {"from": alice})
    assert invoker.balance() == 0
    assert alice.balance() == start_balance


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


def test_move_all_erc20_out_when_no_balance(alice, mock_erc20, invoker, cmove):
    calldata_move_all_out = cmove.moveAllERC20Out.encode_input(mock_erc20.address, alice)
    invoker.invoke([cmove.address], [calldata_move_all_out], {"from": alice})
    assert mock_erc20.balanceOf(invoker.address) == 0
    assert mock_erc20.balanceOf(alice) == 0


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
        mock_deflationary_erc20.address, amount, False
    )
    invoker.invoke([cmove.address], [calldata_move_deflationary_in], {"from": alice})
    assert mock_deflationary_erc20.balanceOf(alice) == 0
    assert mock_deflationary_erc20.balanceOf(invoker) == amount * 0.90


def test_fail_move_deflationary_erc20_in(alice, mock_deflationary_erc20, invoker, cmove):
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
        mock_deflationary_erc20.address, alice, amount, False
    )
    invoker.invoke([cmove.address], [calldata_move_deflationary_out], {"from": alice})
    assert mock_deflationary_erc20.balanceOf(alice) == amount * 0.90
    assert mock_deflationary_erc20.balanceOf(invoker) == 0


def test_fail_move_deflationary_erc20_out(alice, mock_deflationary_erc20, invoker, cmove):
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
        mock_deflationary_erc20.address, alice, False
    )
    invoker.invoke([cmove.address], [calldata_move_all_deflationary_out], {"from": alice})
    assert mock_deflationary_erc20.balanceOf(alice) == amount * 0.90
    assert mock_deflationary_erc20.balanceOf(invoker) == 0


def test_fail_move_all_deflationary_erc20_out(alice, mock_deflationary_erc20, invoker, cmove):
    amount = 100 * 1e18
    mock_deflationary_erc20.mint(invoker.address, amount, {"from": alice})
    calldata_move_all_deflationary_out = cmove.moveAllERC20Out.encode_input(
        mock_deflationary_erc20.address, alice
    )
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_move_all_deflationary_out], {"from": alice})


# Rebasing tokens
# These tests are generally handled by the above tests,
# but the following tests enforce that we have tested rebase tokens explicitly
# to account for any unexpected rounding errors


@pytest.fixture(scope="module")
def rebase_setup(mock_rebasing_erc20, alice, bob, deployer, invoker):
    mock_rebasing_erc20.set_pooled_eth(5, {"from": deployer})
    mock_rebasing_erc20.mint(alice, 4, {"from": deployer})
    mock_rebasing_erc20.mint(bob, 3, {"from": deployer})
    mock_rebasing_erc20.approve(invoker, 100, {"from": alice})
    yield mock_rebasing_erc20


def test_rebase_move_in(rebase_setup, alice, cmove, invoker):
    rebase_token = rebase_setup
    calldata_move = cmove.moveERC20In.encode_input(rebase_token.address, 2)
    with brownie.reverts("CMove: Deflationary token"):
        invoker.invoke([cmove.address], [calldata_move], {"from": alice})
    calldata_move = cmove.moveERC20In.encode_input(rebase_token.address, 2, False)
    invoker.invoke([cmove.address], [calldata_move], {"from": alice})
    assert rebase_token.balanceOf(invoker) == 1
    assert rebase_token.balanceOf(alice) == 1
